"""Fresh 910: correct only private, newly built driver deployment paths."""
from pathlib import Path
import subprocess

base = Path(__file__).resolve().parent
out = base/'payload-910'; assert not out.exists(); out.mkdir()
script = r'''
from pathlib import Path
import subprocess,shutil,gzip,hashlib,json,struct,tempfile
root=Path('/home/zoinve/harmony-virgl-883');work=root/'driver-rpath-910';work.mkdir()
local=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment');out=local/'payload-910'
ram=work/'ramroot';shutil.copytree(root/'allocator-backend-909/ramroot',ram,symlinks=True)
def text_section(p):
 data=p.read_bytes();assert data[:5]==b'\x7fELF\x02'
 shoff=struct.unpack_from('<Q',data,40)[0];size,count,names=struct.unpack_from('<HHH',data,58)
 hdr=struct.unpack_from('<IIQQQQIIQQ',data,shoff+names*size);strings=data[hdr[4]:hdr[4]+hdr[5]]
 for i in range(count):
  h=struct.unpack_from('<IIQQQQIIQQ',data,shoff+i*size)
  name=strings[h[0]:].split(b'\0',1)[0]
  if name==b'.text':return hashlib.sha256(data[h[4]:h[4]+h[5]]).hexdigest()
 raise AssertionError('missing text section')
changes=[]
for p in sorted((ram/'gpu883-libs').rglob('*')):
 if not p.is_file() or p.is_symlink() or '.so' not in p.name or p.name=='libc++_shared.so':continue
 if p.read_bytes()[:4]!=b'\x7fELF':continue
 before=text_section(p)
 old=subprocess.check_output(['patchelf','--print-rpath',str(p)],text=True).strip()
 if old=='/system/lib64/lab-softpipe-167':continue
 assert not old or all(x=='/system/lib64/lab-virgl883' for x in old.split(':')),(p,old)
 needed=subprocess.check_output(['patchelf','--print-needed',str(p)])
 subprocess.run(['patchelf','--set-rpath','/system/lib64/lab-softpipe-167',str(p)],check=True)
 assert text_section(p)==before
 assert subprocess.check_output(['patchelf','--print-needed',str(p)])==needed
 changes.append(dict(path=str(p.relative_to(ram)),old=old,text_sha256=before))
assert any(x['path'].endswith('/gbm/dri_gbm.so') for x in changes)
(out/'rpath-changes.json').write_text(json.dumps(changes,indent=2))
'''
original = (base/'build-gpu-frontend-payload.py').read_text()
archive = 'def entry(' + original.split('def entry(',1)[1].split("'''",1)[0]
archive = archive.replace("['init','gpu-frontend-probe']", "['init','gpu-frontend-probe','gpu903-allocator-probe']")
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=script+archive,text=True,check=True)
