"""Compile and package offline only; never install an entry, mount, or reboot."""
from pathlib import Path
import hashlib
import json
import subprocess

base = Path(__file__).resolve().parent
report = base.parent / 'reports/baremetal-diagnostic-init-001.json'
assert not report.exists()
sources = ['baremetal-diagnostic-core.c', 'baremetal-diagnostic-core.h', 'baremetal-diagnostic-init.c']
hashes = {name: hashlib.sha256((base / name).read_bytes()).hexdigest() for name in sources}
work = '/home/zoinve/harmony-virgl-883/baremetal-diagnostic-init-001'
build = r'''
from pathlib import Path
import subprocess,json,hashlib
base=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
work=Path(WORK); assert not work.exists(); work.mkdir()
for name,digest in HASHES.items():
 data=(base/name).read_bytes(); assert hashlib.sha256(data).hexdigest()==digest
 (work/name).write_bytes(data)
subprocess.run(['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-Werror',
 str(work/'baremetal-diagnostic-core.c'),str(work/'baremetal-diagnostic-init.c'),
 '-o',str(work/'diagnostic-init')],check=True)
p=work/'diagnostic-init'; data=p.read_bytes()
assert data[:4]==b'\x7fELF' and int.from_bytes(data[18:20],'little')==183
print(json.dumps(dict(binary_sha256=hashlib.sha256(data).hexdigest(),binary_bytes=len(data),source_hashes=HASHES)))
'''.replace('WORK', repr(work)).replace('HASHES', repr(hashes))
r = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=build,
                   text=True, capture_output=True, check=True, timeout=120)
binary = json.loads(r.stdout)
remote = '/mnt/harmony-lab/work/native-diagnostic-init-001'
guard = r'''
from pathlib import Path
import subprocess,json
mount=json.loads(subprocess.check_output(['findmnt','-J','-T','/mnt/harmony-lab','-o','SOURCE,UUID'],text=True))['filesystems'][0]
assert mount['source']=='/dev/nvme0n1p4' and mount['uuid']=='00029cdd-1748-4d2f-b73b-8e8164922098'
p=Path(REMOTE); assert not p.exists(); p.mkdir()
'''.replace('REMOTE', repr(remote))
subprocess.run(['ssh', 'matebook', 'python3 -'], input=guard, text=True, check=True, timeout=30)
unc = Path('//wsl.localhost/Debian' + work)
for name in sources + ['diagnostic-init']:
    subprocess.run(['scp', str(unc / name), 'matebook:' + remote + '/' + name], check=True, timeout=60)
payload = r'''
from pathlib import Path
import gzip,hashlib,json,subprocess,stat
dest=Path(REMOTE); meta=META
for name,digest in meta['source_hashes'].items():
 assert hashlib.sha256((dest/name).read_bytes()).hexdigest()==digest
exe=dest/'diagnostic-init'; data=exe.read_bytes()
assert hashlib.sha256(data).hexdigest()==meta['binary_sha256']
exe.chmod(0o755)
# Real execution outside PID1 must refuse before mounts/modules/storage writes.
p=subprocess.run([str(exe)],text=True,capture_output=True,timeout=5)
assert p.returncode==77 and 'requires PID 1' in p.stderr,(p.returncode,p.stdout,p.stderr)
parent=Path('/mnt/harmony-lab/work/native-initramfs-base-002/diagnostic-base.cpio.gz')
expected='ff0a661c831f950ebad0cd69c91b21d999bffce6f2bc49601e2cb7253ab5219c'
assert hashlib.sha256(parent.read_bytes()).hexdigest()==expected
raw=gzip.decompress(parent.read_bytes())
def parse(raw):
 entries={}; pos=0
 while True:
  start=pos; h=raw[pos:pos+110]; assert h[:6]==b'070701' and len(h)==110
  values=[int(h[6+i*8:14+i*8],16) for i in range(13)]
  size,ns=values[6],values[11]
  name=raw[pos+110:pos+110+ns-1].decode(); assert raw[pos+110+ns-1]==0
  begin=(pos+110+ns+3)&~3; pos=(begin+size+3)&~3
  if name=='TRAILER!!!': return entries,start
  assert name not in entries and len(raw[begin:begin+size])==size
  entries[name]=(values[1],values[2],values[3],raw[begin:begin+size])
before,trailer=parse(raw); assert 'init' not in before and './init' not in before
def member(name,mode,body,ino):
 encoded=name.encode()+b'\0'
 fields=[ino,mode,0,0,1,0,len(body),0,0,0,0,len(encoded),0]
 result=b'070701'+b''.join(f'{x:08x}'.encode() for x in fields)+encoded
 result+=b'\0'*((-len(result))%4); result+=body
 return result+b'\0'*((-len(result))%4)
updated=raw[:trailer]+member('init',stat.S_IFREG|0o755,data,0x100000)+member('TRAILER!!!',0,b'',0)
after,_=parse(updated)
assert all(after[name]==value for name,value in before.items()) and len(after)==len(before)+1
assert after['init']==(stat.S_IFREG|0o755,0,0,data)
archive=dest/'diagnostic-init.cpio.gz'; assert not archive.exists()
archive.write_bytes(gzip.compress(updated,compresslevel=6,mtime=0))
assert parse(gzip.decompress(archive.read_bytes()))[0]==after
assert hashlib.sha256(parent.read_bytes()).hexdigest()==expected
result=dict(destination=str(dest),archive=str(archive),archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
 archive_bytes=archive.stat().st_size,entries=len(after),base_entries_unchanged=True,base_archive_unchanged=True,
 archive_roundtrip_verified=True,non_pid1_refusal_verified=True,source_hashes=meta['source_hashes'],
 binary_sha256=meta['binary_sha256'],contains_init=True,offline_candidate_only=True,
 boot_entry_installed=False,modules_loaded=False,native_boot_attempted=False,
 hardware_recovery_verified=False,harmony_compatibility_verified=False)
(dest/'manifest.json').write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))
'''.replace('REMOTE', repr(remote)).replace('META', repr(binary))
r = subprocess.run(['ssh', 'matebook', 'python3 -'], input=payload, text=True,
                   capture_output=True, timeout=120)
stdout = report.with_suffix('.stdout')
stderr = report.with_suffix('.stderr')
assert not stdout.exists() and not stderr.exists()
stdout.write_text(r.stdout, encoding='utf-8')
stderr.write_text(r.stderr, encoding='utf-8')
r.check_returncode()
result = json.loads(r.stdout)
report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2))
