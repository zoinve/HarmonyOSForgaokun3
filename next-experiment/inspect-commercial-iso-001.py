"""Read the user-selected installer; never execute its installer or write a device."""
import subprocess

payload = r'''
from pathlib import Path
import hashlib,json,re,shutil,subprocess
iso=Path('/mnt/d/lab/HarmonyOSForMatebookego/L410-HarmonyOS-Installer-20261029.iso')
work=Path('/home/zoinve/harmony-virgl-883/commercial61-iso-001')
local=Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/commercial61-iso-001')
assert not work.exists() and not local.exists()
assert shutil.disk_usage(work.parent).free>40*1024**3
work.mkdir();local.mkdir()
listing=subprocess.check_output(['isoinfo','-R','-i',str(iso),'-l'],text=True)
(local/'iso-directory.txt').write_text(listing)
parts=[]
for line in listing.splitlines():
 m=re.search(r'\s(\d+)\s+\w+\s+\d+\s+\d+\s+\[\s*(\d+)\s+00\]\s+(payload\.squashfs\.part-(\d+))',line)
 if m:parts.append(dict(name=m[3],index=int(m[4]),bytes=int(m[1]),offset=int(m[2])*2048))
parts.sort(key=lambda p:p['index'])
assert [p['index'] for p in parts]==list(range(8)),parts
digest=hashlib.sha256()
with iso.open('rb') as src,(work/'payload.squashfs').open('xb') as dst:
 for part in parts:
  src.seek(part['offset']);left=part['bytes'];h=hashlib.sha256()
  while left:
   data=src.read(min(left,8*1024*1024));assert data
   dst.write(data);h.update(data);digest.update(data);left-=len(data)
  part['sha256']=h.hexdigest()
for name in ['README.txt','boot/grub/grub.cfg','boot/initrd.img']:
 p=work/Path(name).name
 with p.open('xb') as out:subprocess.run(['isoinfo','-R','-i',str(iso),'-x','/'+name],stdout=out,check=True)
 if p.suffix!='.img':shutil.copyfile(p,local/p.name)
with iso.open('rb') as f:iso_sha=hashlib.file_digest(f,'sha256').hexdigest()
r=dict(iso=str(iso),iso_bytes=iso.stat().st_size,iso_sha256=iso_sha,
 payload_sha256=digest.hexdigest(),parts=parts,installer_executed=False,
 device_written=False,boot_entries_changed=False,original_images_modified=False)
for p in [work/'result.json',local/'result.json']:p.write_text(json.dumps(r,indent=2))
print(json.dumps(r,indent=2))
'''
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=1200).returncode)
