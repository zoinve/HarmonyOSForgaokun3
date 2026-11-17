"""Preserve readable files and exact per-file errors; never repair the original LAB."""
from pathlib import Path
import subprocess,json,tarfile,io,hashlib
root=Path(__file__).resolve().parents[1]/'reports/commercial61-native-004/runtime-evidence-partial'
assert not root.exists()
code=r'''
from pathlib import Path
import subprocess,tarfile,io,json,hashlib,sys
mount=Path('/mnt/commercial-readable-004');mount.mkdir(exist_ok=True)
assert subprocess.run(['findmnt','-rn','-S','/dev/nvme0n1p4'],capture_output=True).returncode!=0
subprocess.run(['mount','-t','ext4','-o','ro,noload,nodev,nosuid,noexec','/dev/nvme0n1p4',str(mount)],check=True)
try:
 runs=list(mount.glob('commercial61-native-004-*'));assert len(runs)==1,[str(p) for p in runs]
 files={};errors={}
 with tarfile.open(fileobj=sys.stdout.buffer,mode='w|') as tf:
  for p in runs[0].iterdir():
   try:
    if not p.is_file():continue
    data=p.read_bytes()
   except OSError as e:errors[p.name]=str(e);continue
   files[p.name]=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
   t=tarfile.TarInfo(p.name);t.size=len(data);tf.addfile(t,io.BytesIO(data))
 print(json.dumps(dict(run=runs[0].name,files=files,unreadable=errors,read_only_noload=True,original_partition_replayed=False)),file=sys.stderr)
finally:subprocess.run(['umount',str(mount)],check=True)
'''
r=subprocess.run(['ssh','matebook','sudo -n python3 -'],input=code.encode(),capture_output=True,timeout=180)
assert r.returncode==0,r.stderr.decode(errors='replace')
m=json.loads(r.stderr);root.mkdir();(root/'original-readable.tar').open('xb').write(r.stdout)
raw=root/'raw';raw.mkdir()
with tarfile.open(fileobj=io.BytesIO(r.stdout)) as tf:
 for t in tf:
  assert t.isfile() and '/' not in t.name and t.name not in ['.','..']
  data=tf.extractfile(t).read();assert hashlib.sha256(data).hexdigest()==m['files'][t.name]['sha256']
  (raw/t.name).open('xb').write(data)
(root/'retrieval-manifest.json').open('x').write(json.dumps(m,indent=2))
print(json.dumps(dict(run=m['run'],readable_files=len(m['files']),unreadable_files=len(m['unreadable']),hashes_matched=True)))
