"""Read-only original NativeWindow export gate; no target ABI acceptance."""
import subprocess
payload=r'''
from pathlib import Path
import hashlib,json,re,subprocess
r=Path('/home/zoinve/harmony-virgl-883');w=r/'commercial-graphics-014'
local=Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/commercial-graphics-014')
original=w/'original-libsurface.z.so';assert not original.exists()
img=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')
subprocess.run(['debugfs','-R','dump /system/lib64/chipset-sdk-sp/libsurface.z.so '+str(original),str(img)],check=True,capture_output=True)
assert original.stat().st_size>100000
exports={l.split()[-1].split('@')[0] for l in subprocess.check_output(['aarch64-linux-gnu-nm','-D','--defined-only',str(original)],text=True).splitlines() if l.split()}
source=(w/'egl-commercial-014.cpp').read_text()
required=set(re.findall(r'NATIVE\(\w+, "([^"]+)"\)',source))
assert len(required)==7 and not required-exports,sorted(required-exports)
result=dict(original_surface_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),required_nativewindow_exports=sorted(required),all_seven_original_exports_present=True,source_image_written=False,target_accessed=False,target_abi_verified=False,desktop_verified=False)
for p in [w/'nativewindow-export-audit.json',local/'nativewindow-export-audit.json']:p.open('x').write(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=60).returncode)
