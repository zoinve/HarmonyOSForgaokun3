"""Read-only checks; never boot or run a completed operational experiment."""
from pathlib import Path
import subprocess

payload = r'''
from pathlib import Path
import gzip,hashlib,json,stat,subprocess,shutil
root=Path('/home/zoinve/harmony-virgl-883/native-original-graphics-boot-001')
assert (root/'result.json').is_file(), 'native original-service boot candidate is missing'
d=json.loads((root/'result.json').read_text())
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for row in d['artifacts']:
 p=root/row['name'];assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes']
outer=(root/'init.c').read_text();inner=(root/'bootstrap.c').read_text()
assert 'sleep(180); reboot(RB_AUTOBOOT)' in outer
assert 'CLONE_NEWPID|CLONE_NEWNS|CLONE_NEWNET|SIGCHLD' in outer
assert 'MS_RDONLY|MS_NODEV|MS_NOSUID|MS_NOEXEC, "noload"' in outer
assert 'LO_FLAGS_READ_ONLY|LO_FLAGS_AUTOCLEAR' in outer
assert 'kill(child,SIGKILL)' in outer and 'snapshot();' in outer
assert 'native-mesa-offscreen' not in outer and 'native-identity-read' not in outer
assert 'harmony.native_original=1' in outer and 'strstr(text,"Matebook E Go")' in outer
assert 'strstr(buffer, "Matebook E Go")' in inner
assert 'ohos.boot.hardware=matebookego' in inner
assert 'dummy-virt' not in inner and 'ohos.boot.hardware=hmos.emulator' not in inner
assert 'lab-freedreno003' in inner and 'harmony-mesa' not in inner
assert 'S_ISBLK(st.st_mode)' in inner and 'strncmp(entry->d_name, "loop", 4)' in inner
assert 'services_ready=0' in inner
assert 'setparam bootevent' not in inner
assert 'buffer[0] != \'0\'' in inner
assert 'platform_libcxx_replaced=0' in inner
assert json.loads((root/'board-init.cfg').read_text())=={'jobs':[]}
fstab=(root/'board-fstab').read_text()
assert '/dev/block/vd' not in fstab and '/dev/nvme' not in fstab
for i in range(4):assert '/dev/block/loop'+str(i) in fstab
guard_count=0
if shutil.which('qemu-aarch64'):
 for binary in ['init','bootstrap']:
  r=subprocess.run(['qemu-aarch64',str(root/binary)],capture_output=True,text=True,timeout=5)
  assert r.returncode==77,(binary,r.returncode,r.stderr)
  assert 'requires' in r.stderr
  guard_count+=1
print(json.dumps(dict(artifacts_verified=len(d['artifacts']),emulated_non_pid1_refusals=guard_count,
 native_guard_checks_required=guard_count==0,
 original_service_runtime_verified=False,desktop_verified=False)))
'''

if __name__ == '__main__':
    r = subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120)
    raise SystemExit(r.returncode)
