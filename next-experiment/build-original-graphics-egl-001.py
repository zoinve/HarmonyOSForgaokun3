"""Build the reference NativeWindow bridge; retain only a scoped Mesa closure."""
import subprocess

payload = r'''
from pathlib import Path
import hashlib,json,runpy,subprocess,re,stat
project=Path('/mnt/d/lab/HarmonyOSForMatebookego')
root=Path('/home/zoinve/harmony-virgl-883')
work=root/'original-graphics-egl-001'
report=project/'reports/original-graphics-egl-001'
assert not work.exists() and not report.exists()
work.mkdir();report.mkdir();bundle=work/'bundle';bundle.mkdir()
mesa=bundle/'harmony-mesa';mesa.mkdir()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
ref=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/graphics')
refs={str(p):sha(p) for p in ref.rglob('*') if p.is_file()}
images=json.loads((project/'reports/baremetal-sdk-original-init-qemu-048/result.json').read_text())['original_images']
parser=runpy.run_path(str(project/'next-experiment/build-composer-parser-001.py'))
parent=project/'next-experiment/official-composer-service-957/initramfs.cpio.gz'
assert sha(parent)==parser['PARENT_HASH']
entries=parser['unpack'](parent.read_bytes())
base='system/lib64/lab-softpipe-167/'
allowed={'libEGL.so.1','libGLESv1_CM.so.1','libGLESv2.so.2','libgbm.so.1',
 'libdrm.so.2','libexpat.so.1','libgallium-25.0.1.so','libglapi.so.0',
 'libz.so.1','libzstd.so.1','liblzma.so.5','libelf.so.1'}
platform={'libc.so','libc++.so','libunwind.so','libz.so','libz.z.so','libexpat.z.so'}
def resolve(name):
 seen=set()
 while True:
  assert name not in seen and '/' not in name and name not in ['.','..'],name
  seen.add(name);mode,body=entries[base+name]
  if not stat.S_ISLNK(mode):
   assert stat.S_ISREG(mode) and body[:6]==b'\x7fELF\x02\x01' and body[18:20]==b'\xb7\0'
   return body
  name=body.decode()
queue=['libEGL.so.1','libGLESv1_CM.so.1','libGLESv2.so.2','libgbm.so.1','libdrm.so.2']
selected={};unresolved_dependencies=set();external=set()
while queue:
 name=queue.pop(0)
 if name in selected:continue
 assert name in allowed,name
 body=resolve(name);p=mesa/name;p.write_bytes(body)
 dyn=subprocess.check_output(['readelf','-dW',str(p)],text=True)
 (report/(name+'.dynamic.txt')).write_text(dyn)
 needed=re.findall(r'\(NEEDED\).*?\[(.*?)\]',dyn)
 assert not any(n in ['libc.so.6','libstdc++.so.6','libgcc_s.so.1'] for n in needed),needed
 selected[name]=dict(path=str(p),sha256=sha(p),bytes=len(body),needed=needed)
 for n in needed:
  if n in platform:external.add(n)
  elif n in allowed and base+n in entries:queue.append(n)
  else:unresolved_dependencies.add(n)
with (report/'mesa-closure.json').open('x') as f:json.dump(dict(files=selected,external=sorted(external),unresolved_dependencies=sorted(unresolved_dependencies)),f,indent=2)
assert not unresolved_dependencies,sorted(unresolved_dependencies)
# Existing SDK dependencies are evidence, not replacement bundle members.
for name in sorted(external):
 if name=='libc.so':continue # Original guest musl loader is part of the unchanged baseline.
 found=False
 for directory in ['/lib64/','/lib64/chipset-pub-sdk/','/lib64/platformsdk/']:
  dest=work/('sdk-'+name)
  p=subprocess.run(['debugfs','-R','dump '+directory+name+' '+str(dest),images['system.img']['path']],capture_output=True)
  if dest.exists() and dest.read_bytes()[:4]==b'\x7fELF':found=True;break
 assert found,('Original SDK dependency missing',name)
backend='gbm/dri_gbm.so';body=entries[base+backend][1]
assert body[:4]==b'\x7fELF'
(mesa/'gbm').mkdir();(mesa/backend).write_bytes(body)
backend_dyn=subprocess.check_output(['readelf','-dW',str(mesa/backend)],text=True)
(report/'dri_gbm.dynamic.txt').write_text(backend_dyn)
assert all(n in selected or n in platform for n in re.findall(r'\(NEEDED\).*?\[(.*?)\]',backend_dyn))
source=(ref/'egl_window_bridge.cpp').read_text()
assert source.count('/system/lib64/aurora-mesa/libEGL.so.1')==1
adapted=source.replace('/system/lib64/aurora-mesa/libEGL.so.1','/system/lib64/harmony-mesa/libEGL.so.1')
assert adapted.replace('/system/lib64/harmony-mesa/libEGL.so.1','/system/lib64/aurora-mesa/libEGL.so.1')==source
cpp=work/'egl_window_bridge.cpp';cpp.write_text(adapted)
tool=root/'window-bridge/toolchain';prefix=root/'prefix/system'
includes=['-I'+str(ref),'-I'+str(ref/'include'),'-I'+str(prefix/'include'),'-I'+str(prefix/'include/libdrm')]
commands=[
 [str(tool/'ohos-cc'),'-fPIC','-O2','-Wall','-Wextra','-Werror',*includes,'-c',str(ref/'drm_device.c'),'-o',str(work/'drm_device.o')],
 [str(tool/'ohos-platform-cxx'),'-shared','-fPIC','-O2','-std=c++17','-Wall','-Wextra','-DEGL_EGLEXT_PROTOTYPES',*includes,str(cpp),str(work/'drm_device.o'),str(mesa/'libGLESv2.so.2'),str(mesa/'libgbm.so.1'),str(mesa/'libdrm.so.2'),'-ldl','-Wl,--no-undefined,-soname,libEGL_impl.so','-Wl,-Bsymbolic-functions','-Wl,-rpath,/system/lib64/harmony-mesa','-o',str(bundle/'libEGL_impl.so')]
]
for i,cmd in enumerate(commands):
 p=subprocess.run(cmd,capture_output=True)
 (report/('compile-%d.stdout'%i)).write_bytes(p.stdout)
 (report/('compile-%d.stderr'%i)).write_bytes(p.stderr)
 assert p.returncode==0,(cmd,p.stderr.decode(errors='replace'))
files=[]
for p in sorted(bundle.rglob('*')):
 if not p.is_file():continue
 dyn=subprocess.check_output(['readelf','-dW',str(p)],text=True)
 needed=re.findall(r'\(NEEDED\).*?\[(.*?)\]',dyn)
 assert all(n in selected or n in platform for n in needed),needed
 files.append(dict(name=str(p.relative_to(bundle)),path=str(p),sha256=sha(p),bytes=p.stat().st_size,needed=needed))
original_images_unchanged=all(sha(Path(r['path']))==r['sha256'] for r in images.values())
reference_files_unchanged=all(sha(Path(p))==h for p,h in refs.items())
assert original_images_unchanged and reference_files_unchanged
result=dict(files=files,commands=commands,original_images_unchanged=original_images_unchanged,
 reference_files_unchanged=reference_files_unchanged,reference_files=refs,platform_abi='std::__h',
 source_change='One absolute Mesa dlopen path only; reference source unmodified',
 external_original_sdk_dependencies=sorted(external),runtime_executed=False,
 service_credentials_modified=False,physical_board_test=False)
for dest in [work/'result.json',report/'result.json']:
 with dest.open('x') as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
'''

compile(payload, 'original-graphics-egl-001', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=240).returncode)
