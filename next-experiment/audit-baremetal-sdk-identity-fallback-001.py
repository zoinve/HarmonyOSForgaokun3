"""Read-only SDK disassembly; extract copies only into a fresh inspection directory."""
from pathlib import Path
import json
import subprocess

payload = r'''
from pathlib import Path
import hashlib,json,subprocess,struct
root=Path('/home/zoinve/harmony-virgl-883')
out=root/'baremetal-sdk-identity-fallback-001';assert not out.exists();out.mkdir()
image=Path('/mnt/d/Download/pc_all_arm/Image');raw=image.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='c0b82fc9dca3b83b5e8201a376b9920d9b53b2be158e8f790835ad3f1d56bbe9'
system='/mnt/d/Download/pc_all_arm/system.img'
names={'libipc_single.z.so':'/system/lib64/platformsdk/libipc_single.z.so',
       'libappspawn_common.z.so':'/system/lib64/appspawn/common/libappspawn_common.z.so',
       'libspm_module_parser.z.so':'/system/lib64/libspm_module_parser.z.so',
       'appspawn':'/system/bin/appspawn'}
files={}
for name,source in names.items():
 p=out/name
 r=subprocess.run(['debugfs','-R','dump '+source+' '+str(p),system],capture_output=True,text=True,timeout=25)
 if not p.is_file():
  files[name]=dict(source=source,error=r.stdout+r.stderr);continue
 data=p.read_bytes();assert data[:4]==b'\x7fELF',source
 nm=subprocess.check_output(['aarch64-linux-gnu-nm','-D','-C',str(p)],text=True)
 dis=subprocess.check_output(['aarch64-linux-gnu-objdump','-d','-C',str(p)],text=True)
 (out/(name+'.nm')).write_text(nm);(out/(name+'.dis')).write_text(dis)
 files[name]=dict(source=source,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),
  identity_symbols=[l for l in nm.splitlines() if any(x in l.lower() for x in ['token','spm','feature','binder'])])
# On-disk pointers can be zero until RELA entries are applied. Record candidates,
# rather than treating zero-filled table entries as unsupported commands.
relocations=[]
for pos in range(0,len(raw)-24,8):
 offset,info,addend=struct.unpack_from('<QQQ',raw,pos)
 if (offset & 0xffffff) in range(0xf980b8,0xf98100) and info==1027:
  relocations.append(dict(file_offset=hex(pos),target=hex(offset),addend=hex(addend)))
result=dict(image_sha256=hashlib.sha256(raw).hexdigest(),files=files,
 driver_table_relocations=relocations,inspection_directory=str(out),
 images_modified=False,kernel_patch_applied=False,reboot_requested=False)
(out/'audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
'''

if __name__ == '__main__':
    out = Path(__file__).resolve().parent.parent / 'reports/baremetal-sdk-identity-fallback-001.json'
    assert not out.exists()
    result = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                            input=payload, capture_output=True, text=True, timeout=180)
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    out.write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps(data, indent=2))
