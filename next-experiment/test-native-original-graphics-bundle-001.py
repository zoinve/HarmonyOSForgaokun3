"""Independently inspect the inert native package; never execute ARM64 code."""
import subprocess

payload = r'''
from pathlib import Path
import hashlib,json,re,subprocess
root=Path('/home/zoinve/harmony-virgl-883')
work=root/'native-original-graphics-bundle-001'
assert (work/'result.json').is_file(), 'Native original-service Freedreno bundle is not built'
d=json.loads((work/'result.json').read_text());bundle=work/'bundle'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
native=json.loads((root/'baremetal-mesa-freedreno-003/result.json').read_text())
assert native['gallium_driver']=='freedreno' and native['kernel_driver']=='msm' and native['build_success']
expected={str(Path(r['path']).relative_to('system/lib64/lab-freedreno003')):r['sha256']
 for r in native['artifacts'] if r['path'].startswith('system/lib64/lab-freedreno003/')}
rows={r['target']:r for r in d['files']}
for name in ['libEGL.so.1','libGLESv1_CM.so.1','libGLESv2.so.2','libgbm.so.1','libgallium-25.0.1.so','gbm/dri_gbm.so']:
 p=bundle/'system/lib64/lab-freedreno003'/name
 assert p.is_file() and not p.is_symlink(), name
 original=(root/'baremetal-mesa-freedreno-003/stage/system/lib64/lab-freedreno003'/name).resolve()
 assert sha(p)==expected[str(original.relative_to(root/'baremetal-mesa-freedreno-003/stage/system/lib64/lab-freedreno003'))], name
assert b'/system/lib64/lab-freedreno003/gbm' in (bundle/'system/lib64/lab-freedreno003/libgbm.so.1').read_bytes(), 'Compiled GBM backend directory must exist without an alias'
external={'libc.so','libc++.so','libbuffer_handle.z.so'}
for target,row in rows.items():
 p=bundle/target.lstrip('/')
 assert p.is_file() and not p.is_symlink(),('Missing package file',target)
 assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes'],target
 body=p.read_bytes();assert body[:6]==b'\x7fELF\x02\x01' and body[18:20]==b'\xb7\0',target
 dyn=subprocess.check_output(['readelf','-dW',str(p)],text=True)
 needed=re.findall(r'\(NEEDED\).*?\[(.*?)\]',dyn)
 assert not set(needed)&{'libc.so.6','libstdc++.so.6','libgcc_s.so.1'},(target,needed)
 paths=re.findall(r'\((?:RUNPATH|RPATH)\).*?\[(.*?)\]',dyn)
 search=[p.parent]+[bundle/q.lstrip('/') for path in paths for q in path.split(':')]
 for name in needed:
  assert name in external or any((directory/name).is_file() for directory in search),(target,name,paths)
assert not (bundle/'system/lib64/libc++.so').exists(), 'Never overwrite platform C++ runtime'
assert '/system/lib64/lab-freedreno003/libc++_shared.so' in rows
bridge=bundle/'system/lib64/libEGL_impl.so'
assert b'/system/lib64/lab-freedreno003/libEGL.so.1\0' in bridge.read_bytes()
symbols=subprocess.check_output(['nm','-D','-C',str(bridge)],text=True)
assert 'std::__h::' in symbols and 'std::__ndk1::' not in symbols and 'std::__1::' not in symbols
bridge_dyn=subprocess.check_output(['readelf','-dW',str(bridge)],text=True)
assert '[libc++.so]' in bridge_dyn and '[libc++_shared.so]' not in bridge_dyn
for row in d['source_files']:
 assert sha(Path(row['path']))==row['sha256'],row['path']
for target in ['libGLESv1_impl.so','libGLESv2_impl.so','libGLESv3_impl.so']:
 p=bundle/'system/lib64'/target
 assert p.is_symlink() and p.resolve().is_relative_to(bundle.resolve()) and p.is_file(),target
assert d['runtime_executed'] is False and d['boot_entries_modified'] is False
assert d['desktop_verified'] is False and d['physical_board_test'] is False
assert not any('/system/lib64/lab-virgl883/' in target or '/system/lib64/lab-softpipe-167/' in target for target in rows)
print(json.dumps(dict(files_verified=len(rows),native_mesa_files_verified=6,
 dependency_closure_verified=True,compiled_gbm_backend_path_present=True,
 platform_libcxx_preserved=True,bridge_platform_cpp_abi_verified=True,
 runtime_executed=False),indent=2))
'''

if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)
