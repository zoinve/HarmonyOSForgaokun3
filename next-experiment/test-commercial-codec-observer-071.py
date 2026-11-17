"""Compile observer helpers and admit only exact diagnostic archive delta."""
from pathlib import Path
import ast
import json
import runpy
import subprocess

b=Path(__file__).resolve().parent
root=Path('/home/zoinve/harmony-virgl-883')
h=runpy.run_path(str(b/'commercial-codec-observer-071.py'))
work=root/'commercial-codec-observer-test-071-r2'
work.mkdir()
prefix=r'''
#define _GNU_SOURCE
#include <dirent.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <time.h>
#include <unistd.h>
#include <assert.h>
static int commercial_diag_fd003=1;
static int read_text(const char *path,char *out,size_t size){
 int fd=open(path,O_RDONLY|O_CLOEXEC);if(fd<0)return -1;
 ssize_t n=read(fd,out,size-1);close(fd);if(n<0)return -1;out[n]=0;return 0;
}
static ssize_t read_path(const char *path,char *out,size_t size){
 if(read_text(path,out,size))return -1;
 return (ssize_t)strlen(out);
}
static void commercial_stream043(const char *p,unsigned s,long pid,unsigned n){
 (void)p;(void)s;(void)pid;(void)n;
}
'''
source=prefix+h['helper']()+h['INNER']+r'''
int main(void){
 errno=EDOM;codec071_inventory(0,(long)getpid());assert(errno==EDOM);
 codec071_inventory(12,(long)getpid());assert(errno==EDOM);
 assert(hw071_find_service(getpid())==0);
 assert(hw071_resolve(getpid())==-1);
 hw071_tick(getpid(),1);
 return 0;
}
'''
(work/'test.c').open('x').write(source)
command=['gcc','-O2','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',str(work/'test.c'),'-o',str(work/'test')]
compiled=subprocess.run(command,capture_output=True)
(work/'compile.stderr').open('xb').write(compiled.stderr)
assert compiled.returncode==0,compiled.stderr.decode(errors='replace')
tested=subprocess.run([str(work/'test')],capture_output=True)
(work/'test.stdout').open('xb').write(tested.stdout)
(work/'test.stderr').open('xb').write(tested.stderr)
assert tested.returncode==0,tested.stderr.decode(errors='replace')
old=runpy.run_path(str(b/'build-commercial-native-070.py'))
new=runpy.run_path(str(b/'build-commercial-native-071.py'))
assert new['inner']==h['inner'](old['inner'])
assert new['outer']==h['outer'](old['outer']).replace('commercial61-native-070','commercial61-native-071').replace('COMMERCIAL070','COMMERCIAL071')
helper=h['helper']()
assert 'attr.bp_type=HW_BREAKPOINT_X' in helper and 'attr.sample_regs_user=0x7f' in helper
assert not any(s in helper for s in ['PTRACE_','/mem"','process_vm_readv','HW_BREAKPOINT_W','HW_BREAKPOINT_R;'])
assert 'fclose(maps);if(!address)continue;' in helper
assert 'if(!hw071_addresses[spec])continue;' in helper
tree=ast.parse(runpy.run_path(str(b/'build-native-return-overlay-033.py'))['payload'])
helpers={}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),'archive-helpers','exec'),helpers)
before=helpers['parse'](root/'commercial61-native-070/initrd.img')
after=helpers['parse'](root/'commercial61-native-071/initrd.img')
assert set(before)==set(after)
changed=sorted(n for n in before if before[n]!=after[n])
assert changed==['init','native-target/bootstrap'],changed
manifest=dict(exact_observer_source_delta=True,all_other_archive_members_unchanged=True,
    exact_delta_from_070=changed,original_resource_files_unchanged=True,
    execute_only_register_observations=True,compiled_helpers_passed=True,
    address_and_undefined_sanitizers_passed=True,original_service_credentials_unchanged=True,
    specs=h['specifications'](),live_private_objects_read=False,instruction_replacement=False,
    runtime_return_values_verified=False,desktop_verified=False)
with (b.parent/'reports/commercial61-native-071/admission-test.json').open('x') as out:
    json.dump(manifest,out,indent=2)
print(json.dumps(manifest,indent=2))
