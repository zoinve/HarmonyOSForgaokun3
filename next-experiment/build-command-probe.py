"""Generate a fresh RAM-only boot probe; never edit a historical payload."""
from pathlib import Path
import hashlib
import json
import subprocess

base = Path(__file__).resolve().parent
out = base / 'payload-873'
remote = '/home/zoinve/.local/share/harmony-arm64-kvm-lab/command-probe-873'
assert not out.exists()
source = (base / 'init.c').read_text()
anchor = 'int main(void) {'
assert source.count(anchor) == 1
probe = r'''
#define BOUNDED_SHELL_LIBRARY
#include "bounded-shell.c"
static void command_probe(void) {
    sleep(120);
    puts("LAB873_PROBE_ENTER root_observer_only=1 commands_drop_to_shell=1");fflush(stdout);
    int identity=lab_shell_run("identity",
        "echo LAB873_SHELL_ENTER; id; cat /proc/self/attr/current; grep CapEff /proc/self/status",
        10,"/system/bin/sh");
    if (identity) {printf("LAB873_ABORT identity_rc=%d\n",identity);fflush(stdout);_exit(0);}
    lab_shell_run("ability-before","/system/bin/aa dump -e -u 100",20,"/system/bin/sh");
    int start=lab_shell_run("sceneboard-start",
        "/system/bin/aa start -b com.ohos.sceneboard -a com.ohos.sceneboard.MainAbility -m pc_sceneboard",
        30,"/system/bin/sh");
    sleep(30);
    if (!start) {
        lab_shell_run("guide-stop","/system/bin/aa force-stop com.huawei.hmos.hwstartupguide",30,"/system/bin/sh");
    } else {
        printf("LAB873_GUIDE_STOP_NOT_ATTEMPTED start_rc=%d\n",start);fflush(stdout);
    }
    sleep(20);
    lab_shell_run("ability-after","/system/bin/aa dump -e -u 100; ps -A | grep -E 'sceneboard|hwstartupguide|render_service|foundation'",20,"/system/bin/sh");
    lab_shell_run("hilog-tail","/system/bin/hilog -x -d | tail -n 250",20,"/system/bin/sh");
    puts("LAB873_PROBE_DONE desktop_not_assumed=1");fflush(stdout);_exit(0);
}

'''
source = source.replace(anchor, probe + anchor)
anchor = '    char *args[]={"/system/bin/init","--second-stage",NULL};'
assert source.count(anchor) == 1
source = source.replace(anchor, '    pid_t probe=fork(); if(probe<0)die("command probe fork"); if(!probe)command_probe();\n' + anchor)
out.mkdir()
(out / 'init.c').write_text(source)
subprocess.run(['scp', str(out / 'init.c'), str(base / 'bounded-shell.c'), 'matebook:' + remote + '/'], check=True)
subprocess.run(['ssh', 'matebook', f'gcc -Wall -Wextra -Werror -O2 -static {remote}/init.c -o {remote}/init'], check=True)
# A minimal newc archive is written directly, without depending on a host cpio package.
script = r'''
from pathlib import Path
import gzip,hashlib,json
p=Path(REMOTE)
def entry(name,data,mode,ino):
 n=name.encode()+b'\0'
 fields=[ino,mode,0,0,1,0,len(data),0,0,0,0,len(n),0]
 b=b'070701'+b''.join(f'{v:08x}'.encode() for v in fields)+n
 b+=b'\0'*(-len(b)%4);b+=data;b+=b'\0'*(-len(data)%4)
 return b
raw=entry('init',(p/'init').read_bytes(),0o100755,1)+entry('TRAILER!!!',b'',0,2)
target=p/'initramfs.cpio.gz'
assert not target.exists()
target.write_bytes(gzip.compress(raw,mtime=0))
print(json.dumps({'remote':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}))
'''.replace('REMOTE', repr(remote))
r = subprocess.run(['ssh', 'matebook', 'python3 -'], input=script, text=True, capture_output=True, check=True)
manifest = json.loads(r.stdout)
(out / 'manifest.json').write_text(json.dumps(manifest, indent=2))
subprocess.run(['scp', 'matebook:' + manifest['remote'], str(out / 'initramfs.cpio.gz')], check=True)
assert hashlib.sha256((out / 'initramfs.cpio.gz').read_bytes()).hexdigest() == manifest['sha256']
print(json.dumps(manifest))
