"""Own FD690 hardware libraries only; commercial init, services and runtimes remain original."""
import subprocess,sys
render_launcher='''#!/system/bin/sh
set -eu
unset LD_PRELOAD VK_ICD_FILENAMES LIBGL_ALWAYS_SOFTWARE
export LD_LIBRARY_PATH=/system/lib64/lab-commercial013:/vendor/lib64/harmony-graphics${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
export GALLIUM_DRIVER=freedreno
exec /system/bin/render_service "$@" >>/data/local/tmp/l410-vulkan-r18/render_service.boot.log 2>&1
'''
host_launcher='''#!/system/bin/sh
set -eu
unset LD_PRELOAD
export LD_LIBRARY_PATH=/vendor/lib64/harmony-graphics:/system/lib64/lab-commercial013${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}
exec /vendor/bin/hdf_devhost "$@"
'''
payload='resume016='+repr('--resume-build' in sys.argv)+'\nrender_launcher='+repr(render_launcher)+'\nhost_launcher='+repr(host_launcher)+r'''
from pathlib import Path
import hashlib,json,subprocess
root=Path('/home/zoinve/harmony-virgl-883')
work=root/'commercial-graphics-bundle-016'
local=Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/commercial-graphics-bundle-016')
if resume016:
 assert work.is_dir() and local.is_dir() and not (work/'result.json').exists()
else:
 assert not work.exists() and not local.exists()
 work.mkdir();local.mkdir()
tree=work/'tree';tree.mkdir(exist_ok=resume016)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
records=[]
def add(target,data,source,mode=0o644):
 p=tree/target.lstrip('/');p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists():assert resume016 and p.read_bytes()==data,p
 else:
  with p.open('xb') as f:f.write(data)
 p.chmod(mode)
 records.append(dict(target=target,bytes=len(data),sha256=sha(p),source=source,mode=mode))
mesa=root/'commercial-mesa-013'
mm=json.loads((mesa/'result.json').read_text());assert mm['build_success']
for item in mm['artifacts']:
 path=item['path']
 if not path.startswith('system/lib64/lab-commercial013/') or '/pkgconfig/' in path:continue
 p=mesa/'stage'/path;assert sha(p)==item['sha256']
 if p.read_bytes()[:4]!=b'\x7fELF':continue
 add('/'+path,p.read_bytes(),str(p))
# Mesa stage symlinks are serialized as actual ELF bytes, with explicit sonames.
for soname in ['libEGL.so.1','libgbm.so.1','libGLESv2.so.2','libGLESv1_CM.so.1','libgallium-25.0.1.so','gbm/dri_gbm.so']:
 target='/system/lib64/lab-commercial013/'+soname
 if any(x['target']==target for x in records):continue
 p=mesa/'stage'/target.lstrip('/');assert p.is_file(),p
 add(target,p.read_bytes(),str(p.resolve()))
graphics=root/'commercial-graphics-014';gm=json.loads((graphics/'result.json').read_text())
assert not gm['sdk_system_libraries_used']
for name,h in gm['graphics_sha256'].items():assert sha(graphics/name)==h
for target,name in [('/vendor/lib64/libdisplay_composer_vdi_impl.z.so','libdisplay_composer_vdi_impl.z.so'),('/system/lib64/libEGL_impl.so','libEGL_impl.so')]:
 add(target,(graphics/name).read_bytes(),str(graphics/name))
allocator=root/'commercial-allocator-015';am=json.loads((allocator/'result.json').read_text())
assert not am['sdk_system_libraries_used']
p=allocator/'libdisplay_buffer_vdi_impl.z.so';assert sha(p)==am['sha256']
add('/vendor/lib64/libdisplay_buffer_vdi_impl.z.so',p.read_bytes(),str(p))
drm=root/'original-graphics-provider-002/bundle/libdrm.so.2'
assert drm.read_bytes()[:4]==b'\x7fELF'
add('/vendor/lib64/harmony-graphics/libdrm.so.2',drm.read_bytes(),str(drm))
add('/system/lib64/lab-commercial013/libdrm.so.2',drm.read_bytes(),str(drm))
for target,soname in [('libGLESv3_impl.so','libGLESv2.so.2'),('libGLESv2_impl.so','libGLESv2.so.2'),('libGLESv1_impl.so','libGLESv1_CM.so.1')]:
 p=mesa/'stage/system/lib64/lab-commercial013'/soname
 add('/system/lib64/'+target,p.read_bytes(),str(p.resolve()))
add('/system/bin/l410-launch-render-service-vulkan-r18-v1.sh',render_launcher.encode(),'own MateBook hardware launcher',0o755)
for n in ['composer','allocator']:
 add('/vendor/bin/l410_launch_'+n+'_host.sh',host_launcher.encode(),'own MateBook hardware launcher',0o755)
image=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p110-sys_prod.img')
before=subprocess.check_output(['debugfs','-R','cat /etc/param/hw_defaults.para',str(image)],stderr=subprocess.DEVNULL)
old=b'persist.sys.graphic.GpuApitype=1';new=b'persist.sys.graphic.GpuApitype=0'
assert before.count(old)==1
after=before.replace(old,new,1);assert after.replace(new,old,1)==before
add('/sys_prod/etc/param/hw_defaults.para',after,'original commercial parameter, only GPU API selection changed')
(local/'original-hw_defaults.para').write_bytes(before)
# All dependencies must be own hardware code or the original commercial system.
for item in records:
 p=tree/item['target'].lstrip('/')
 if p.read_bytes()[:4]==b'\x7fELF':
  deps=subprocess.check_output(['aarch64-linux-gnu-readelf','-d',str(p)],text=True)
  assert 'libc++_shared.so' not in deps
 assert p.name not in ['libc.so','libc++.so','libc++_shared.so']
result=dict(files=records,sdk_system_libraries_used=False,original_service_definitions_changed=False,
 original_parameter_other_lines_unchanged=True,gpu_api_parameter_changes={'persist.sys.graphic.GpuApitype':['1','0']},
 compiler_headers_not_runtime_payload=True,original_images_modified=False,deployed=False,
 target_graphics_abi_verified=False,desktop_verified=False)
for p in [work/'result.json',local/'result.json']:
 with p.open('x') as f:json.dump(result,f,indent=2)
print(json.dumps(dict(files=len(records),bytes=sum(x['bytes'] for x in records),sdk_system_libraries_used=False,target_runtime_verified=False)))
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)
