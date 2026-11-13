"""Compile reference VDIs for the original service graph, not a private probe."""
import subprocess

payload = r'''
from pathlib import Path
import hashlib,json,runpy,shutil,subprocess,re
project=Path('/mnt/d/lab/HarmonyOSForMatebookego')
root=Path('/home/zoinve/harmony-virgl-883')
work=root/'original-graphics-provider-001'
report=project/'reports/original-graphics-provider-001'
assert not work.exists() and not report.exists()
work.mkdir();report.mkdir();bundle=work/'bundle';bundle.mkdir()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
ref=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/graphics')
refs={str(p):sha(p) for p in ref.rglob('*') if p.is_file()}
images=json.loads((project/'reports/baremetal-sdk-original-init-qemu-048/result.json').read_text())['original_images']
handle=root/'baremetal-buffer-handle-audit-001/original-2.so'
assert sha(handle)=='9c3ab7c3c83e074d0238814153752656c28b56202f833ad07f34b2cffd640912'
parser=runpy.run_path(str(project/'next-experiment/build-composer-parser-001.py'))
parent=project/'next-experiment/official-composer-service-957/initramfs.cpio.gz'
assert sha(parent)==parser['PARENT_HASH']
entries=parser['unpack'](parent.read_bytes())
drm=entries['system/lib64/lab-softpipe-167/libdrm.so.2'][1]
(bundle/'libdrm.so.2').write_bytes(drm)
tool=root/'window-bridge/toolchain';prefix=root/'prefix/system'
includes=['-I'+str(ref/'include'),'-I'+str(prefix/'include'),'-I'+str(prefix/'include/libdrm')]
commands=[
 [str(tool/'ohos-cc'),'-fPIC','-O2','-Wall','-Wextra','-Werror',*includes,'-c',str(ref/'drm_device.c'),'-o',str(work/'drm_device.o')],
 [str(tool/'ohos-platform-cxx'),'-shared','-fPIC','-O2','-std=c++17','-Wall','-Wextra',*includes,str(ref/'composer.cpp'),str(work/'drm_device.o'),str(bundle/'libdrm.so.2'),'-Wl,--no-undefined,-soname,libdisplay_composer_vdi_impl.z.so','-Wl,-rpath,/vendor/lib64/harmony-graphics','-o',str(bundle/'libdisplay_composer_vdi_impl.z.so')],
 [str(tool/'ohos-platform-cxx'),'-shared','-fPIC','-O2','-std=c++17','-Wall','-Wextra',*includes,str(ref/'buffer_vdi.cpp'),str(work/'drm_device.o'),str(bundle/'libdrm.so.2'),str(handle),'-Wl,--no-undefined,-soname,libdisplay_buffer_vdi_impl.z.so','-Wl,-rpath,/vendor/lib64/harmony-graphics','-o',str(bundle/'libdisplay_buffer_vdi_impl.z.so')]
]
for i,cmd in enumerate(commands):
 p=subprocess.run(cmd,capture_output=True)
 (report/('compile-%d.stdout'%i)).write_bytes(p.stdout)
 (report/('compile-%d.stderr'%i)).write_bytes(p.stderr)
 assert p.returncode==0,(cmd,p.stderr.decode(errors='replace'))
files=[]
for p in sorted(bundle.iterdir()):
 body=p.read_bytes();assert body[:6]==b'\x7fELF\x02\x01' and body[18:20]==b'\xb7\0'
 dyn=subprocess.check_output(['readelf','-dW',str(p)],text=True)
 (report/(p.name+'.dynamic.txt')).write_text(dyn)
 needed=re.findall(r'\(NEEDED\).*?\[(.*?)\]',dyn)
 assert not any(x in ['libc.so.6','libstdc++.so.6','libgcc_s.so.1'] for x in needed),needed
 exports=subprocess.check_output(['aarch64-linux-gnu-nm','-D','--defined-only',str(p)],text=True)
 (report/(p.name+'.exports.txt')).write_text(exports)
 if 'buffer_vdi' in p.name:assert 'CreateDisplayBufferVdi' in exports
 if 'composer_vdi' in p.name:
  slots=json.loads((project/'reports/composer-sdk7-loader-slots-951.json').read_text())
  assert all(re.search(r'\b'+re.escape(row['name'])+r'$',exports,re.M) for row in slots if row['mandatory'])
 files.append(dict(name=p.name,path=str(p),bytes=p.stat().st_size,sha256=sha(p),needed=needed))
original_images_unchanged=all(sha(Path(row['path']))==row['sha256'] for row in images.values())
reference_files_unchanged=all(sha(Path(p))==h for p,h in refs.items())
assert original_images_unchanged and reference_files_unchanged
result=dict(files=files,commands=commands,original_images_unchanged=original_images_unchanged,
 reference_files_unchanged=reference_files_unchanged,reference_files=refs,
 original_handle_sha256=sha(handle),platform_abi='std::__h',
 runtime_executed=False,service_credentials_modified=False,physical_board_test=False,
 purpose='Original HDF composer/allocator graph VDI replacement, virtual display only')
for dest in [work/'result.json',report/'result.json']:
 with dest.open('x') as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
'''

compile(payload, 'original-graphics-provider-001', 'exec')
if __name__ == '__main__':
    result = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=payload,
                            text=True, timeout=240)
    raise SystemExit(result.returncode)
