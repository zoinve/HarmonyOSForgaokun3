"""Build HarmonyMac's unchanged public SAMgr probe with original commercial libraries."""
import subprocess
payload=r'''
from pathlib import Path
import hashlib,json,re,subprocess,shutil,posixpath
root=Path('/home/zoinve/harmony-virgl-883');base=Path('/mnt/d/lab/HarmonyOSForMatebookego')
reference=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816')
work=root/'commercial-reference-probe-036-r3';local=base/'reports/commercial-reference-probe-036'
assert not work.exists() and not (local/'result.json').exists()
work.mkdir();local.mkdir(exist_ok=True);runtime=work/'runtime';runtime.mkdir()
source=reference/'ports/tests/samgr-service-probe.cpp'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source_sha=sha(source);shutil.copyfile(source,work/source.name)
image=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')
records=[]
def resolve(origin):
 for _ in range(16):
  info=subprocess.check_output(['debugfs','-R','stat '+origin,str(image)],stderr=subprocess.DEVNULL,text=True)
  match=re.search(r'Fast link dest: "([^"]+)"',info)
  if not match:return origin
  target=match[1]
  origin=posixpath.normpath(target if target.startswith('/') else posixpath.join(posixpath.dirname(origin),target))
  assert origin.startswith('/') and not origin.startswith('/../')
 raise RuntimeError('Original library symlink loop: '+origin)
def extract(name):
    p=runtime/name
    if p.exists():return p
    for directory in ['/system/lib64/chipset-sdk-sp','/system/lib64/chipset-sdk','/system/lib64/platformsdk','/system/lib64/chipset-pub-sdk','/system/lib64','/system/lib64/ndk']:
        origin=directory+'/'+name
        resolved=resolve(origin)
        data=subprocess.check_output(['debugfs','-R','cat '+resolved,str(image)],stderr=subprocess.DEVNULL)
        if data.startswith(b'\x7fELF'):
            p.write_bytes(data)
            records.append(dict(name=name,image_path=origin,resolved_image_path=resolved,sha256=sha(p)))
            return p
    raise RuntimeError('Original commercial library missing: '+name)
queue=['libsamgr_proxy.z.so','libutils.z.so','libc++.so','libc.so'];seen=set()
while queue:
 name=queue.pop(0)
 if name in seen:continue
 seen.add(name);p=extract(name)
 dynamic=subprocess.check_output(['aarch64-linux-gnu-readelf','-d',str(p)],text=True)
 queue.extend(re.findall(r'\(NEEDED\).*?\[(.*?)\]',dynamic))
manifest=json.loads((base/'reports/commercial-graphics-014/result.json').read_text())
command=manifest['commands'][0][:manifest['commands'][0].index('-shared')]
headers=root/'reference-start-036-headers'
for directory in [headers/'systemabilitymgr_samgr/interfaces/innerkits/samgr_proxy/include',headers/'commonlibrary_c_utils/base/include',headers/'communication_ipc/interfaces/innerkits/ipc_core/include']:
 command+=['-I'+str(directory)]
command+=['-O2','-Wall','-Wextra','-Wno-deprecated-declarations',str(work/source.name),str(runtime/'libsamgr_proxy.z.so'),str(runtime/'libutils.z.so'),str(runtime/'libc++.so'),str(runtime/'libc.so'),'-ldl','-Wl,-rpath-link,'+str(runtime),'-o',str(work/'samgr-service-probe')]
with (work/'link.stdout').open('xb') as out,(work/'link.stderr').open('xb') as err:
 result=subprocess.run(command,stdout=out,stderr=err,timeout=120)
if result.returncode:raise RuntimeError((work/'link.stderr').read_text())
trace=(work/'link.stdout').read_text()
assert not any('/sdk/' in line and line.strip().endswith('.so') for line in trace.splitlines())
assert sha(source)==source_sha==sha(work/source.name)
dynamic=subprocess.check_output(['aarch64-linux-gnu-readelf','-d',str(work/'samgr-service-probe')],text=True)
assert 'libc++_shared.so' not in dynamic
result=dict(reference_revision='f23a5d73f86ef0e45d3e7ac879a0605049a3c9ad',reference_source=str(source),source_sha256=source_sha,source_byte_identical=True,command=command,original_commercial_libraries=records,header_provenance=json.loads((headers/'provenance.json').read_text()),probe_sha256=sha(work/'samgr-service-probe'),sdk_runtime_libraries_used=False,original_images_modified=False,target_runtime_verified=False,desktop_verified=False)
(work/'result.json').write_text(json.dumps(result,indent=2))
for name in ['samgr-service-probe.cpp','link.stdout','link.stderr','result.json']:shutil.copyfile(work/name,local/name)
print(json.dumps(result,indent=2))
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=240).returncode)
