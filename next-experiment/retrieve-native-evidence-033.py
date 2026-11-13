"""Read-only noload retrieval after the single unattended boot, no journal replay."""
from pathlib import Path
import subprocess,tarfile,io,json,hashlib
root=Path(__file__).resolve().parent.parent/'reports/native-original-graphics-boot-033'
dest=root/'runtime-evidence';assert not dest.exists()
payload=r'''
from pathlib import Path
import subprocess,hashlib,json,sys
mount=Path('/mnt/harmony-return-audit-033');mount.mkdir(exist_ok=True)
assert subprocess.run(['findmnt','-rn','--source','/dev/nvme0n1p4'],capture_output=True).returncode!=0
subprocess.run(['mount','-t','ext4','-o','ro,noload,nodev,nosuid,noexec','/dev/nvme0n1p4',str(mount)],check=True)
try:
 runs=list(mount.rglob('native-interactive-033-*'));assert len(runs)==1,[str(p) for p in runs]
 run=runs[0]
 files={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in run.iterdir() if p.is_file()}
 print(json.dumps(dict(run=run.name,files=files,read_only_noload=True)),file=sys.stderr,flush=True)
 subprocess.run(['tar','-C',str(run),'-cf','-','.'],check=True)
finally:subprocess.run(['umount',str(mount)],check=True)
'''
r=subprocess.run(['ssh','matebook','sudo -n python3 -'],input=payload.encode(),capture_output=True,timeout=180)
assert r.returncode==0,r.stderr.decode(errors='replace')
manifest=json.loads(r.stderr.decode().splitlines()[0])
dest.mkdir();raw=dest/'raw';raw.mkdir()
with (dest/'original.tar').open('xb') as f:f.write(r.stdout)
with tarfile.open(fileobj=io.BytesIO(r.stdout)) as tf:
 for m in tf.getmembers():
  if m.isdir():continue
  name=m.name.removeprefix('./');assert m.isfile() and '/' not in name and name not in ['.','..']
  data=tf.extractfile(m).read();assert hashlib.sha256(data).hexdigest()==manifest['files'][name]['sha256']
  with (raw/name).open('xb') as f:f.write(data)
with (dest/'retrieval-manifest.json').open('x') as f:json.dump(manifest,f,indent=2)
print(json.dumps(dict(run=manifest['run'],files=len(manifest['files']),all_remote_hashes_matched=True,original_partition_replayed=False)))
