"""Reproduce unchanged 159 log binding/key copy in an Ubuntu-only private namespace."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'next-experiment'
BUILD = Path('/home/zoinve/harmony-virgl-883/live-debug-storage-fixture-160')
REPORT = ROOT / 'reports/live-debug-storage-fixture-160'
REMOTE = '/home/zoinve/.local/share/harmony-arm64-kvm-lab/live-debug-storage-fixture-160'
SSH = ['/mnt/c/Windows/System32/OpenSSH/ssh.exe','-i','C:/Users/39255/.ssh/id_ed25519_opencode_matebook',
       '-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','HostKeyAlias=192.168.10.128',
       '-o','ConnectTimeout=8','zoinve@192.168.10.128','sudo -n python3 -']

DRIVER = r'''
int main(void)
{
    if (geteuid() || getpid() != 1) return 77;
    if (mount(NULL,"/",NULL,MS_REC | MS_PRIVATE,NULL) ||
        mount("tmpfs",ROOT159,"tmpfs",MS_NOSUID | MS_NODEV,"mode=0700,size=1m")) return 78;
    const char *directories[] = {"/logs","/etc","/etc/diag"};
    for (unsigned i=0;i<3;++i) {
        char path[512]; snprintf(path,sizeof(path),"%s%s",ROOT159,directories[i]);
        if (mkdir(path,0700)) return 79;
    }
    int source = open(ROOT159 "/source",O_RDWR | O_CREAT | O_EXCL | O_CLOEXEC,0600);
    if (source < 0 || write(source,"synthetic-log-only\n",19) != 19 || dup2(source,196) < 0 || dup2(source,197) < 0) return 80;
    const char *logs[] = {ROOT159 "/logs/hilog",ROOT159 "/logs/native"};
    for (unsigned i=0;i<2;++i) {
        int out = open(logs[i],O_CREAT | O_WRONLY | O_EXCL | O_CLOEXEC,0600);
        if (out < 0) return 81;
        close(out);
    }
    errno=0; int first=bind_log159(196,logs[0]), first_errno=errno;
    errno=0; int second=bind_log159(197,logs[1]), second_errno=errno;
    errno=0; int key=key_copy159(), key_errno=errno;
    int readonly=0, live=0;
    if (!first && !second) {
        errno=0; int prohibited=open(logs[0],O_WRONLY | O_APPEND | O_CLOEXEC);
        readonly=prohibited < 0 && errno==EROFS;
        if (prohibited >= 0) close(prohibited);
        int reader=open(logs[0],O_RDONLY | O_CLOEXEC);
        char value[32]={0};
        if (write(source,"append\n",7)==7 && reader>=0 && pread(reader,value,7,19)==7 && !memcmp(value,"append\n",7)) live=1;
        if (reader>=0) close(reader);
    }
    printf("{\"hilog_status\":%d,\"hilog_errno\":%d,\"native_status\":%d,\"native_errno\":%d,\"key_status\":%d,\"key_errno\":%d,\"readonly_enforced\":%s,\"append_visible\":%s}\n",
        first,first_errno,second,second_errno,key,key_errno,readonly?"true":"false",live?"true":"false");
    close(source);close(196);close(197);
    return 0;
}
'''

REMOTE_RUN = r'''
from pathlib import Path
import base64,hashlib,json,os,subprocess
root=Path(REMOTE_ROOT)
assert os.geteuid()==0 and not root.exists()
root.mkdir(mode=0o700);(root/'root').mkdir(mode=0o700)
before=Path('/proc/self/mountinfo').read_text()
boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
key=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/live-debug-156/root/etc/diag/host_ed25519')
def key_metadata():
 info=key.stat()
 return (info.st_dev,info.st_ino,info.st_mode,info.st_uid,info.st_gid,info.st_size,info.st_mtime_ns,info.st_ctime_ns)
key_before=key_metadata()
data=base64.b64decode(BINARY_BASE64,validate=True)
assert hashlib.sha256(data).hexdigest()==BINARY_SHA256
binary=root/'fixture';binary.write_bytes(data);binary.chmod(0o700)
run=subprocess.run(['/usr/bin/timeout','--kill-after=2','15','unshare','--mount','--pid','--fork',str(binary)],capture_output=True,text=True,timeout=20)
after=Path('/proc/self/mountinfo').read_text()
key_after=key_metadata()
result=dict(fixture_only=True,harmony_boot_performed=False,returncode=run.returncode,stdout=run.stdout,stderr=run.stderr,
 boot_id=boot,boot_unchanged=boot==Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
 outer_mounts_unchanged=before==after,ram_root_empty_after_exit=not any((root/'root').iterdir()),
 original_key_metadata_unchanged=key_before==key_after,private_key_exported=False,raw_harmony_logs_read=False)
(root/'result.json').open('x').write(json.dumps(result,indent=2))
print(json.dumps(result))
assert run.returncode==0 and result['boot_unchanged'] and result['outer_mounts_unchanged'] and result['ram_root_empty_after_exit'] and result['original_key_metadata_unchanged']
'''


if __name__ == '__main__':
    assert not BUILD.exists() and not REPORT.exists(), 'preserve numbered fixture evidence'
    BUILD.mkdir();REPORT.mkdir()
    source = Path('/home/zoinve/harmony-virgl-883/commercial61-native-159/live-debug-launcher-159.c').read_text()
    start = source.index('static int bind_log159(')
    end = source.index('static int address159(',start)
    functions = source[start:end]
    headers = '#define _GNU_SOURCE\n#include <errno.h>\n#include <fcntl.h>\n#include <stdio.h>\n#include <string.h>\n#include <sys/mount.h>\n#include <sys/stat.h>\n#include <sys/statvfs.h>\n#include <unistd.h>\n'
    headers += '#define ROOT159 ' + json.dumps(REMOTE + '/root') + '\n'
    headers += '#define KEY159 "/home/zoinve/.local/share/harmony-arm64-kvm-lab/live-debug-156/root/etc/diag/host_ed25519"\n'
    fixture = BUILD / 'fixture.c'
    fixture.open('x').write(headers + functions + DRIVER)
    binary = BUILD / 'fixture'
    compiled = subprocess.run(['aarch64-linux-gnu-gcc','-static','-Os','-s','-Wall','-Wextra','-Werror',str(fixture),'-o',str(binary)],capture_output=True,timeout=60)
    (REPORT / 'compile.stderr').open('xb').write(compiled.stderr)
    assert compiled.returncode==0,compiled.stderr.decode()
    data=binary.read_bytes()
    remote = REMOTE_RUN.replace('REMOTE_ROOT',repr(REMOTE)).replace('BINARY_BASE64',repr(base64.b64encode(data).decode())).replace('BINARY_SHA256',repr(hashlib.sha256(data).hexdigest()))
    completed=subprocess.run(SSH,input=remote,text=True,capture_output=True,timeout=35)
    (REPORT / 'remote.stdout').open('x').write(completed.stdout)
    (REPORT / 'remote.stderr').open('x').write(completed.stderr)
    result=json.loads(completed.stdout)
    result.update(source_functions_sha256=hashlib.sha256(functions.encode()).hexdigest(),
        fixture_source_sha256=hashlib.sha256(fixture.read_bytes()).hexdigest(),binary_sha256=hashlib.sha256(data).hexdigest())
    (REPORT / 'result.json').open('x').write(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
    assert completed.returncode==0,completed.stderr
