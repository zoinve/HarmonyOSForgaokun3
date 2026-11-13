"""Read original ramdisk bootstrap configuration; no mounting, execution or image changes."""
import subprocess

payload=r'''
from pathlib import Path
import gzip,hashlib,json,stat,subprocess
root=Path('/home/zoinve/harmony-virgl-883');work=root/'baremetal-sdk-init-bootstrap-001'
out=Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/baremetal-sdk-init-bootstrap-001.json')
assert not work.exists() and not out.exists();work.mkdir()
image=Path('/mnt/d/Download/pc_all_arm/ramdisk.img');compressed=image.read_bytes();raw=gzip.decompress(compressed)
assert len(raw)<=32*1024**2
entries={};pos=0
while pos+110<=len(raw):
 h=raw[pos:pos+110];assert h[:6] in (b'070701',b'070702')
 fields=[int(h[6+i*8:14+i*8],16) for i in range(13)]
 mode=fields[1];size=fields[6];ns=fields[11];name=raw[pos+110:pos+109+ns].decode();start=(pos+110+ns+3)&~3;pos=(start+size+3)&~3
 if name=='TRAILER!!!':break
 name=name.removeprefix('./');assert name not in entries,name
 entries[name]=dict(mode=mode,data=raw[start:start+size])
result=dict(ramdisk_bytes=len(compressed),ramdisk_sha256=hashlib.sha256(compressed).hexdigest(),entries=len(entries),
 bootstrap_entries={},configuration_files={},executables={},images_modified=False,executed=False)
for name,row in entries.items():
 base=Path(name).name;data=row['data'];kind=stat.S_IFMT(row['mode'])
 if base in ('init','init.cfg','ueventd.config') or 'fstab' in base or name.count('/')<=1:
  result['bootstrap_entries'][name]=dict(mode=oct(row['mode']),bytes=len(data),symlink=data.decode(errors='replace') if kind==stat.S_IFLNK else None)
 if kind==stat.S_IFREG and len(data)<=128*1024 and (base.endswith(('.cfg','.rc')) or 'fstab' in base):
  assert len(result['configuration_files'])<64
  result['configuration_files'][name]=dict(sha256=hashlib.sha256(data).hexdigest(),text=data.decode(errors='replace'))
 if kind==stat.S_IFREG and base in ('init','libload_policy.z.so') and data[:4]==b'\x7fELF':
  p=work/(base+'.elf');assert not p.exists();p.write_bytes(data)
  dynamic=subprocess.check_output(['aarch64-linux-gnu-readelf','-d',str(p)],text=True)
  symbols=subprocess.check_output(['aarch64-linux-gnu-nm','-D','-C',str(p)],text=True)
  strings=subprocess.check_output(['strings','-a',str(p)],text=True).splitlines()
  selected=[s for s in strings if any(x in s.lower() for x in ['fstab','selinux','sepolicy','restorecon','/init.cfg','/system/bin/init','/vendor/','boot_stage','second_stage','load_policy','setcon','enforcing'])]
  result['executables'][name]=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),dynamic=dynamic,
    selected_symbols=[s for s in symbols.splitlines() if any(x in s.lower() for x in ['main','selinux','policy','restorecon','setcon','init'])],selected_strings=selected[:200])
out.write_text(json.dumps(result,indent=2)+'\n');(work/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(dict(entries=result['entries'],bootstrap_entries=result['bootstrap_entries'],configuration_files=list(result['configuration_files']),executables=result['executables']),indent=2))
'''
compile(payload,'sdk-init-bootstrap-audit','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=60)
    raise SystemExit(r.returncode)
