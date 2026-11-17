"""Compile the guarded probe and test numeric parsing without mounting anything."""
from pathlib import Path
import json
import runpy
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'next-experiment'
BUILD=Path('/home/zoinve/harmony-virgl-883')

if __name__ == '__main__':
    work=BUILD/'compat-cgroup-527'
    output=ROOT/'reports/compat-cgroup-527.json'
    assert not work.exists() and not output.exists()
    work.mkdir()
    source=runpy.run_path(str(BASE/'compat-network-helper-526.py'))['SOURCE']
    assert 'setns(fds[i], kinds[i])' in source and '!same(&after, &rootstat)' in source
    probe=(BASE/'native-compat-cgroup-525.c').read_text()
    assert probe.index('unshare(CLONE_NEWNS)')<probe.index('mount("compat525"')
    assert 'finished && !parent_killed' in probe and 'oom_kills>0' in probe
    subprocess.run(['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-x','c','-',
                    '-o',str(work/'network-helper')],input=source,text=True,check=True,timeout=60)
    headers='''#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>
'''
    main=r'''
int main(int argc,char **argv) {
    if(argc!=3)return 2;
    printf("%lld\n",compat525_number(argv[1],!strcmp(argv[2],"-") ? NULL:argv[2]));
    return 0;
}
'''
    subprocess.run(['gcc','-O1','-g','-fsanitize=address,undefined','-x','c','-',
                    '-o',str(work/'parser')],input=headers+probe+main,text=True,check=True,timeout=60)
    cases=[('33554432\n','-',33554432),('max 1\n','max',1),
           ('oom_kill_disable 0\nunder_oom 0\noom_kill 1\n','oom_kill',1),
           ('0\n','-',0),('max -1\n','max',-1),('max 1bad\n','max',-1),
           ('max 9223372036854775808\n','max',-1),('max 1\n','oom_kill',-1),
           ('max_bad 2\nmax 1\n','max',1),('x'*4096,'-',-1)]
    with tempfile.TemporaryDirectory(prefix='compat-parser-527-') as directory:
        path=Path(directory)/'counter'
        for text,field,want in cases:
            path.write_text(text)
            result=subprocess.run([str(work/'parser'),str(path),field],capture_output=True,text=True,timeout=10)
            assert result.returncode==0,(field,result.stderr)
            assert result.stdout.strip()==str(want),(field,result.stdout,want)
    result=dict(arm64_helper_compiled=True,parser_sanitizer_cases=len(cases),
                namespace_guards_retained=True,controllers_mounted=False,
                native_limits_verified=False,platform_application_verified=False)
    with output.open('x') as stream:json.dump(result,stream,indent=2)
    print(json.dumps(result,indent=2))
