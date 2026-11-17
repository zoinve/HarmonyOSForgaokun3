"""Transfer a small public ALSA/UCM closure; never copy host data or credentials."""
from pathlib import Path
import base64
import hashlib
import json
import runpy
import subprocess

ROOT=Path(__file__).resolve().parents[1]
QUERY=r'''
from pathlib import Path
import base64,gzip,hashlib,io,json,os,subprocess,tarfile
assert subprocess.check_output(['uname','-r'],text=True).strip()=='7.1.0-rc3-gaokun3+'
files={}
for name in ['libc.so.6','libm.so.6','libasound.so.2','libdl.so.2','libpthread.so.0','librt.so.1']:
 path=Path('/usr/lib/aarch64-linux-gnu')/name
 assert path.is_file() and path.resolve().is_relative_to('/usr/lib/aarch64-linux-gnu')
 files['lib/'+name]=path.read_bytes()
loader=Path('/lib/ld-linux-aarch64.so.1')
assert loader.is_file()
files['lib/ld-linux-aarch64.so.1']=loader.read_bytes()
root=Path('/usr/share/alsa')
for path in sorted(root.rglob('*')):
 if path.is_file():
  assert path.resolve().is_relative_to(root.resolve()) and path.stat().st_size<1024**2
  files['share/alsa/'+path.relative_to(root).as_posix()]=path.read_bytes()
assert len(files)<3000 and sum(map(len,files.values()))<16*1024**2
archive=io.BytesIO()
with tarfile.open(fileobj=archive,mode='w',format=tarfile.USTAR_FORMAT) as tar:
 for name,data in files.items():
  item=tarfile.TarInfo(name);item.size=len(data);item.mode=0o755 if name.startswith('lib/') else 0o644
  tar.addfile(item,io.BytesIO(data))
packed=gzip.compress(archive.getvalue(),compresslevel=6,mtime=0)
print(json.dumps(dict(payload=base64.b64encode(packed).decode(),sha256=hashlib.sha256(packed).hexdigest(),
 bytes=len(packed),files=len(files),uncompressed_bytes=sum(map(len,files.values())),
 public_system_assets_only=True,host_routes_changed=False,private_keys_exported=False)))
'''
EXTRACT=r'''
from pathlib import Path
import gzip,hashlib,io,json,os,sys,tarfile
root=Path('/home/zoinve/harmony-virgl-883/audio-assets-314')
assert not root.exists()
data=sys.stdin.buffer.read(8*1024**2)
assert hashlib.sha256(data).hexdigest()==expected
with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as tar:
 members=tar.getmembers()
 assert len(members)==count
 for item in members:
  path=Path(item.name)
  assert not path.is_absolute() and '..' not in path.parts and item.isfile()
  assert item.name.startswith(('lib/','share/alsa/'))
 root.mkdir(mode=0o700)
 for item in members:
  path=root/item.name;path.parent.mkdir(parents=True,exist_ok=True)
  with path.open('xb') as stream:stream.write(tar.extractfile(item).read())
  path.chmod(item.mode)
print(json.dumps(dict(extracted_files=len(members),archive_persisted=False)))
'''

if __name__=='__main__':
 output=ROOT/'reports/audio-assets-314.json'
 assert not output.exists()
 ssh=runpy.run_path(str(ROOT/'next-experiment/deploy-settings-data-198.py'))['SSH']
 result=subprocess.run(ssh+['python3 -'],input=QUERY,text=True,capture_output=True,timeout=50)
 assert result.returncode==0,result.stderr
 record=json.loads(result.stdout);packed=base64.b64decode(record.pop('payload'))
 assert len(packed)==record['bytes'] and hashlib.sha256(packed).hexdigest()==record['sha256']
 source='expected='+repr(record['sha256'])+'\ncount='+repr(record['files'])+'\n'+EXTRACT
 done=subprocess.run(['wsl','-d','Debian','--','python3','-c',source],input=packed,capture_output=True,timeout=30)
 assert done.returncode==0,done.stderr.decode(errors='replace')
 record.update(json.loads(done.stdout))
 record['local_root']='/home/zoinve/harmony-virgl-883/audio-assets-314'
 output.open('x').write(json.dumps(record,indent=2))
 print(json.dumps(record,indent=2))
