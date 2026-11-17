"""Recover allowlisted early diagnostics without exporting runtime identities."""
from pathlib import Path
import json
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
runpy.run_path(str(BASE / 'commercial-workflow-123.py'))['configure_local_transport']()
output = BASE.parent / 'reports/commercial61-native-123/cmdline-admission-audit.json'
assert not output.exists()
payload = r'''
from pathlib import Path
import hashlib,json,re,subprocess
mount=Path('/mnt/commercial-early-audit-123')
mount.mkdir(exist_ok=True)
assert subprocess.run(['findmnt','-rn','--source','/dev/nvme0n1p4'],capture_output=True).returncode!=0
subprocess.run(['mount','-t','ext4','-o','ro,noload,nodev,nosuid,noexec','/dev/nvme0n1p4',str(mount)],check=True)
try:
 name='commercial61-native-087-8a37e4cd-deb7-433f-bbb0-fdd51847fba0'
 runs=list(mount.rglob(name));assert len(runs)==1
 run=runs[0];assert run.is_dir() and not run.is_symlink()
 serials=[Path('/sys/class/dmi/id/'+k).read_bytes().strip() for k in ('product_serial','chassis_serial')]
 assert all(len(s)==16 and s.isalnum() for s in serials)
 needles={v for s in serials for v in (s,s.lower(),s.upper())}
 allowed=re.compile(rb'^(?:NATIVE_ORIGINAL001_FAIL |NATIVE_ORIGINAL001_REFUSED |NATIVE_ROOT_NAMESPACE003 |NATIVE_ORIGINAL_START |NATIVE_ORIGINAL_SAMPLE |NATIVE_LOOP |NATIVE_RAM_DATA016 |NATIVE_ORIGINAL_DATA |COMMERCIAL087_TARGET_EXIT |COMMERCIAL001_HANDOFF )')
 files=[]
 for p in sorted(run.glob('phase-*.log')):
  assert p.is_file() and not p.is_symlink()
  data=p.read_bytes();lines=[]
  for line in data.splitlines():
   if not allowed.match(line):continue
   assert len(line)<2048 and not any(n in line for n in needles)
   assert not re.search(rb'(?<![0-9a-fA-F])[0-9a-fA-F]{64}(?![0-9a-fA-F])',line)
   lines.append(line.decode('ascii',errors='strict'))
  required=[b'harmony.commercial=1',b'harmony.original_init_test=1',b'harmony.native_original=1',b'enforcing=0',b'ohos.boot.hardware=matebookego']
  candidates=[line for line in data.splitlines() if b'rdinit=/early-hardware093.sh' in line]
  cmdlines=[dict(bytes=len(line),required_tokens={key.decode():key in line.split() for key in required},initrd_tokens=sum(t.startswith(b'initrd=') for t in line.split())) for line in candidates]
  files.append(dict(name=p.name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),cmdlines=cmdlines))
 assert files
 result=dict(run=name,read_only_noload=True,allowlisted_only=True,physical_serial_guard_passed=True,hex_identity_guard_passed=True,files=files)
finally:
 subprocess.run(['umount',str(mount)],check=True)
print(json.dumps(result))
'''
r = subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','HostName=192.168.10.128','-o','HostKeyAlias=192.168.10.128','matebook','sudo -n python3 -'], input=payload.encode(),capture_output=True,timeout=180)
assert r.returncode == 0, r.stderr.decode(errors='replace')
result=json.loads(r.stdout)
with output.open('x') as stream:
    json.dump(result,stream,indent=2)
print(json.dumps(result['files'][-1],indent=2))
