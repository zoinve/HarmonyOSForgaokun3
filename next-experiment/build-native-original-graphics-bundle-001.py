"""Inert native original-service provider bundle. No deployment, boot or GPU calls."""
import subprocess

payload = r'''
from pathlib import Path
import hashlib,json,re,subprocess,shutil
project=Path('/mnt/d/lab/HarmonyOSForMatebookego')
root=Path('/home/zoinve/harmony-virgl-883')
work=root/'native-original-graphics-bundle-001'
report=project/'reports/native-original-graphics-bundle-001'
assert not work.exists() and not report.exists(), 'Preserve numbered outputs'
native=root/'baremetal-mesa-freedreno-003'
previous=json.loads((native/'result.json').read_text())
assert previous['build_success'] and previous['gallium_driver']=='freedreno' and previous['kernel_driver']=='msm'
stage=native/'stage/system/lib64/lab-freedreno003'
expected={r['path']:r['sha256'] for r in previous['artifacts']}
ref=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/graphics')
tool=root/'window-bridge/toolchain';prefix=root/'prefix/system'
images=json.loads((project/'reports/baremetal-sdk-original-init-qemu-048/result.json').read_text())['original_images']
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
sources={}
def protect(p):
 p=p.resolve();sources[str(p)]=sha(p);return p
for p in [native/'result.json',*ref.rglob('*')]:
 if p.is_file():protect(p)
work.mkdir();report.mkdir();bundle=work/'bundle';bundle.mkdir()
mesa=bundle/'system/lib64/lab-freedreno003';mesa.mkdir(parents=True)
def copy(source,target,expected_sha=None):
 source=protect(source)
 if expected_sha is not None:assert sha(source)==expected_sha,str(source)
 target.parent.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(source,target)
 assert sha(source)==sha(target)
for name in ['libEGL.so.1','libGLESv1_CM.so.1','libGLESv2.so.2','libgbm.so.1','libgallium-25.0.1.so','gbm/dri_gbm.so']:
 source=(stage/name).resolve()
 copy(source,mesa/name,expected[str(source.relative_to(native/'stage'))])
copy(prefix/'lib64/lab-virgl883/libdrm.so.2',mesa/'libdrm.so.2')
old_egl=json.loads((root/'original-graphics-egl-002/result.json').read_text())
runtime=next(r for r in old_egl['files'] if r['name']=='harmony-mesa/libc++_shared.so')
copy(Path(runtime['path']),mesa/'libc++_shared.so',runtime['sha256'])
provider=json.loads((root/'original-graphics-provider-002/result.json').read_text())
for row in provider['files']:
 copy(Path(row['path']),bundle/'vendor/lib64/harmony-graphics'/row['name'],row['sha256'])
source=(ref/'egl_window_bridge.cpp').read_text()
old='/system/lib64/aurora-mesa/libEGL.so.1'
new='/system/lib64/lab-freedreno003/libEGL.so.1'
assert source.count(old)==1
adapted=source.replace(old,new)
assert adapted.replace(new,old)==source
cpp=work/'egl_window_bridge.cpp';cpp.write_text(adapted)
includes=['-I'+str(ref),'-I'+str(ref/'include'),'-I'+str(prefix/'include'),'-I'+str(prefix/'include/libdrm')]
commands=[
 [str(tool/'ohos-cc'),'-fPIC','-O2','-Wall','-Wextra','-Werror',*includes,'-c',str(ref/'drm_device.c'),'-o',str(work/'drm_device.o')],
 [str(tool/'ohos-platform-cxx'),'-shared','-fPIC','-O2','-std=c++17','-Wall','-Wextra','-DEGL_EGLEXT_PROTOTYPES',*includes,str(cpp),str(work/'drm_device.o'),str(mesa/'libGLESv2.so.2'),str(mesa/'libgbm.so.1'),str(mesa/'libdrm.so.2'),'-ldl','-Wl,--no-undefined,-soname,libEGL_impl.so','-Wl,-Bsymbolic-functions','-Wl,-rpath,/system/lib64/lab-freedreno003','-o',str(bundle/'system/lib64/libEGL_impl.so')]
]
for i,cmd in enumerate(commands):
 p=subprocess.run(cmd,capture_output=True)
 (report/f'compile-{i}.stdout').write_bytes(p.stdout)
 (report/f'compile-{i}.stderr').write_bytes(p.stderr)
 assert p.returncode==0,(cmd,p.stderr.decode(errors='replace'))
for name,dest in [('libGLESv1_impl.so','libGLESv1_CM.so.1'),('libGLESv2_impl.so','libGLESv2.so.2'),('libGLESv3_impl.so','libGLESv2.so.2')]:
 (bundle/'system/lib64'/name).symlink_to('lab-freedreno003/'+dest)
rows=[]
for p in sorted(bundle.rglob('*')):
 if not p.is_file() or p.is_symlink():continue
 dyn=subprocess.check_output(['readelf','-dW',str(p)],text=True)
 target='/'+str(p.relative_to(bundle))
 (report/(str(p.relative_to(bundle)).replace('/','_')+'.dynamic.txt')).write_text(dyn)
 needed=re.findall(r'\(NEEDED\).*?\[(.*?)\]',dyn)
 assert not set(needed)&{'libc.so.6','libstdc++.so.6','libgcc_s.so.1'},target
 rows.append(dict(target=target,sha256=sha(p),bytes=p.stat().st_size,needed=needed))
assert all(sha(Path(r['path']))==r['sha256'] for r in images.values()), 'Original SDK image changed'
assert all(sha(Path(p))==h for p,h in sources.items()), 'Protected input changed'
result=dict(files=rows,source_files=[dict(path=p,sha256=h) for p,h in sorted(sources.items())],
 original_images=images,original_images_unchanged=True,commands=commands,
 mesa_driver='freedreno',kernel_driver='msm',platform_abi='std::__h',
 private_mesa_ndk_runtime=True,platform_libcxx_replaced=False,
 compiled_gbm_backend_directory='/system/lib64/lab-freedreno003/gbm',
 source_change='Reference EGL bridge: one absolute Mesa path only; source files unchanged',
 runtime_executed=False,boot_entries_modified=False,physical_board_test=False,
 desktop_verified=False,service_credentials_modified=False,
 activation_requires='Isolated target boot and recovery guard; never run original init or load target policy into Ubuntu',
 physical_modeset_permission_inherited=False)
for dest in [work/'result.json',report/'result.json']:
 with dest.open('x') as f:json.dump(result,f,indent=2)
print(json.dumps(dict(work=str(work),files=len(rows),bytes=sum(r['bytes'] for r in rows),runtime_executed=False)))
'''

if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=240).returncode)
