"""Own open-source hardware allocator, linked only to the commercial runtime."""
import subprocess,sys
payload=r'''
from pathlib import Path
import hashlib,json,subprocess,shutil,sys
r=Path('/home/zoinve/harmony-virgl-883');base=Path('/mnt/d/lab/HarmonyOSForMatebookego')
w=r/'commercial-allocator-015';local=base/'reports/commercial-allocator-015'
if w.exists():assert '--resume-compile' in sys.argv and not (w/'result.json').exists()
else:w.mkdir();local.mkdir();(w/'runtime').mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=r/'commercial-graphics-014';m=json.loads((old/'result.json').read_text())
for n,h in m['runtime_sha256'].items():
 assert sha(old/'runtime'/n)==h
 shutil.copyfile(old/'runtime'/n,w/'runtime'/n)
ref=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/graphics/buffer_vdi.cpp')
original_sha=sha(ref)
text=ref.read_text().replace('info.usage), info.expectedSize);','info.usage), static_cast<size_t>(info.expectedSize));')
text=text.replace('size mismatch got=%u expected=%zu','size mismatch got=%llu expected=%zu')
text=text.replace('request.size, info.expectedSize);','static_cast<unsigned long long>(request.size), static_cast<size_t>(info.expectedSize));')
(w/'buffer-vdi.cpp').write_text(text)
handle=w/'original-commercial-buffer-handle.so'
if not handle.exists():
 image='/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img'
 subprocess.run(['debugfs','-R','dump -p /system/lib64/chipset-sdk-sp/libbuffer_handle.z.so '+str(handle),image],check=True,capture_output=True)
assert handle.stat().st_size==12104
cmd=[x.replace(str(old),str(w)).replace(str(w/'composer-trace.cpp'),str(w/'buffer-vdi.cpp'))
 .replace('libdisplay_composer_vdi_impl.z.so','libdisplay_buffer_vdi_impl.z.so') for x in m['commands'][0]]
cmd+=[str(handle),'-Wno-unused-parameter']
attempt=0
while (w/('link.stdout'+('.'+str(attempt) if attempt else ''))).exists():attempt+=1
suffix='.'+str(attempt) if attempt else ''
with (w/('link.stdout'+suffix)).open('xb') as out,(w/('link.stderr'+suffix)).open('xb') as err:
 result=subprocess.run(cmd,stdout=out,stderr=err,timeout=120)
for n in ['link.stdout','link.stderr']:shutil.copyfile(w/(n+suffix),local/(n+suffix))
assert result.returncode==0,(w/('link.stderr'+suffix)).read_text()
assert sha(ref)==original_sha
data=dict(sha256=sha(w/'libdisplay_buffer_vdi_impl.z.so'),commands=[cmd],reference_source_sha256=original_sha,
 link_trace_file='link.stdout'+suffix,original_buffer_handle_sha256=sha(handle),
 reference_license='HarmonyMac buffer_vdi.cpp source header retained; see original project licensing',
 sdk_system_libraries_used=False,original_commercial_libc_and_libcxx=True,
 original_services_replaced=False,deployed=False,target_abi_verified=False,desktop_verified=False)
for p in [w/'result.json',local/'result.json']:p.open('x').write(json.dumps(data,indent=2))
print(json.dumps(data,indent=2))
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-']+sys.argv[1:],input=payload,text=True,timeout=180).returncode)
