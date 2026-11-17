"""Reproduce inherited-FD bind failure and test same-inode reopening on native ARM64."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'next-experiment'
assert sys.argv[1:] in [[],['--compile-fix-1']]
SUFFIX='-compile-fix-1' if sys.argv[1:] else ''
BUILD=Path('/home/zoinve/harmony-virgl-883/live-debug-log-fixture-163'+SUFFIX)
REPORT=ROOT/('reports/live-debug-log-fixture-163'+SUFFIX)
REMOTE='/home/zoinve/.local/share/harmony-arm64-kvm-lab/live-debug-log-fixture-163'+SUFFIX
SSH=['/mnt/c/Windows/System32/OpenSSH/ssh.exe','-i','C:/Users/39255/.ssh/id_ed25519_opencode_matebook',
 '-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','HostKeyAlias=192.168.10.128',
 '-o','ConnectTimeout=8','zoinve@192.168.10.128','sudo -n python3 -']

DRIVER=r'''
#include <sched.h>
#include <signal.h>
#include <sys/wait.h>

static int worker(void *opaque)
{
    (void)opaque;
    if(getpid()!=1 || mount(NULL,"/",NULL,MS_REC | MS_PRIVATE,NULL) ||
       mount("tmpfs",FIXTURE_ROOT "/ram","tmpfs",MS_NOSUID | MS_NODEV,"mode=0700,size=1m"))return 78;
    const char *paths[]={FIXTURE_ROOT "/ram/old",FIXTURE_ROOT "/ram/new",FIXTURE_ROOT "/ram/native"};
    for(unsigned i=0;i<3;++i){int fd=open(paths[i],O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC,0600);if(fd<0)return 79;close(fd);}
    errno=0;int old=live_storage161_bind(196,paths[0],1),old_errno=errno;
    int first=live_log163_reopen(196,1),first_error=errno;
    int second=live_log163_reopen(197,2),second_error=errno;
    int new_status=first<0 ? -1 : live_storage161_bind(first,paths[1],1);
    int native_status=second<0 ? -1 : live_storage161_bind(second,paths[2],2);
    int readonly=0,live=0;
    if(!new_status && !native_status){
        errno=0;int forbidden=open(paths[1],O_WRONLY | O_APPEND | O_CLOEXEC);
        readonly=forbidden<0 && errno==EROFS;if(forbidden>=0)close(forbidden);
        int writer=open(FIXTURE_ROOT "/interactive-hilog030.log",O_WRONLY | O_APPEND | O_CLOEXEC);
        char data[7];
        if(writer>=0 && write(writer,"append\n",7)==7 && pread(first,data,7,19)==7 && !memcmp(data,"append\n",7))live=1;
        if(writer>=0)close(writer);
    }
    printf("{\"old_bind_status\":%d,\"old_bind_errno\":%d,\"reopen_hilog_ok\":%s,\"reopen_native_ok\":%s,\"hilog_reopen_errno\":%d,\"native_reopen_errno\":%d,\"new_bind_status\":%d,\"native_bind_status\":%d,\"readonly_enforced\":%s,\"append_visible\":%s}\n",
        old,old_errno,first>=0?"true":"false",second>=0?"true":"false",first<0?first_error:0,second<0?second_error:0,
        new_status,native_status,readonly?"true":"false",live?"true":"false");
    fflush(stdout);
    if(first>=0)close(first);
    if(second>=0)close(second);
    return 0;
}

int main(void)
{
    (void)live_storage161_key;
    if(geteuid())return 77;
    int first=open(FIXTURE_ROOT "/interactive-hilog030.log",O_RDONLY | O_CLOEXEC);
    int second=open(FIXTURE_ROOT "/native-source.log",O_RDONLY | O_CLOEXEC);
    if(first<0 || second<0 || dup2(first,196)<0 || dup2(second,197)<0)return 80;
    close(first);close(second);
    static char stack[1024*1024] __attribute__((aligned(16)));
    pid_t pid=clone(worker,stack+sizeof(stack),CLONE_NEWNS | CLONE_NEWPID | SIGCHLD,NULL);
    if(pid<0)return 81;
    int state;
    if(waitpid(pid,&state,0)!=pid || !WIFEXITED(state))return 82;
    close(196);close(197);
    return WEXITSTATUS(state);
}
'''

REMOTE_RUN=r'''
from pathlib import Path
import base64,hashlib,json,os,subprocess
root=Path(REMOTE_ROOT)
assert os.geteuid()==0 and not root.exists()
root.mkdir(mode=0o700);(root/'ram').mkdir(mode=0o700)
for name in ['interactive-hilog030.log','native-source.log']:
 (root/name).open('xb').write(b'synthetic-log-only\n')
 (root/name).chmod(0o600)
before=Path('/proc/self/mountinfo').read_text()
boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
data=base64.b64decode(BINARY_BASE64,validate=True)
assert hashlib.sha256(data).hexdigest()==BINARY_SHA256
binary=root/'fixture';binary.open('xb').write(data);binary.chmod(0o700)
run=subprocess.run(['/usr/bin/timeout','--kill-after=2','15',str(binary)],capture_output=True,text=True,timeout=20)
after=Path('/proc/self/mountinfo').read_text()
result=dict(fixture_only=True,harmony_boot_performed=False,private_keys_read=False,raw_harmony_logs_read=False,
 returncode=run.returncode,stdout=run.stdout,stderr=run.stderr,boot_id=boot,
 boot_unchanged=boot==Path('/proc/sys/kernel/random/boot_id').read_text().strip(),outer_mounts_unchanged=before==after,
 ram_mountpoint_empty=not any((root/'ram').iterdir()))
(root/'result.json').open('x').write(json.dumps(result,indent=2))
print(json.dumps(result))
assert run.returncode==0 and result['boot_unchanged'] and result['outer_mounts_unchanged'] and result['ram_mountpoint_empty']
'''


if __name__=='__main__':
    assert not BUILD.exists() and not REPORT.exists()
    BUILD.mkdir();REPORT.mkdir()
    source='#define _GNU_SOURCE\n#define FIXTURE_ROOT '+json.dumps(REMOTE)+'\n'
    source+='#define LIVE163_HILOG_PREFIX FIXTURE_ROOT "/"\n#define LIVE163_NATIVE_PATH FIXTURE_ROOT "/native-source.log"\n'
    source+='#include "live-debug-log-163.h"\n#include "live-debug-storage-161.h"\n'+DRIVER
    fixture=BUILD/'fixture.c';fixture.open('x').write(source)
    binary=BUILD/'fixture'
    built=subprocess.run(['aarch64-linux-gnu-gcc','-static','-Os','-s','-Wall','-Wextra','-Werror','-I',str(BASE),str(fixture),'-o',str(binary)],capture_output=True,timeout=60)
    (REPORT/'compile.stderr').open('xb').write(built.stderr)
    assert built.returncode==0,built.stderr.decode()
    data=binary.read_bytes()
    remote=REMOTE_RUN.replace('REMOTE_ROOT',repr(REMOTE)).replace('BINARY_BASE64',repr(base64.b64encode(data).decode())).replace('BINARY_SHA256',repr(hashlib.sha256(data).hexdigest()))
    done=subprocess.run(SSH,input=remote,text=True,capture_output=True,timeout=35)
    (REPORT/'remote.stdout').open('x').write(done.stdout);(REPORT/'remote.stderr').open('x').write(done.stderr)
    result=json.loads(done.stdout)
    observation=json.loads(result['stdout'].splitlines()[-1]) if result['returncode']==0 else {}
    passed=observation.get('old_bind_status')==-1 and observation.get('old_bind_errno')==22
    passed=passed and observation.get('new_bind_status')==0 and observation.get('native_bind_status')==0
    passed=passed and observation.get('readonly_enforced') is True and observation.get('append_visible') is True
    result.update(inherited_fd_failure_reproduced_and_reopen_fix_verified=passed,observation=observation,
        source_sha256=hashlib.sha256(fixture.read_bytes()).hexdigest(),binary_sha256=hashlib.sha256(data).hexdigest(),
        log_header_sha256=hashlib.sha256((BASE/'live-debug-log-163.h').read_bytes()).hexdigest())
    (REPORT/'result.json').open('x').write(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
    assert done.returncode==0 and passed,done.stderr
