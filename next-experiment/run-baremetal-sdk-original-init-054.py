"""Original init, HDI services and scoped EGL/Mesa on the isolated virtual GPU."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-053.py')))['payload']
for old, new in [('original-init-qemu-053', 'original-init-qemu-054'),
                 ('harmony-sdk-qemu053-', 'harmony-sdk-qemu054-'),
                 ('original-init-050', 'original-init-054'),
                 ('ORIGINAL_INIT050_', 'ORIGINAL_INIT054_'),
                 ('GRAPHICS050_', 'GRAPHICS054_')]:
    assert old in payload
    payload = payload.replace(old, new)
anchor = "add('TRAILER!!!',0)"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, """egl=json.loads((root/'original-graphics-egl-002/result.json').read_text())
assert egl['platform_abi']=='std::__h' and len(egl['files'])==9
assert egl['mesa_ndk_runtime_scoped'] and not egl['platform_libcxx_replaced']
for directory in ['graphics-egl','graphics-egl/harmony-mesa','graphics-egl/harmony-mesa/gbm']:
 add(directory,stat.S_IFDIR|0o755)
for row in egl['files']:
 p=Path(row['path']);assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
 assert row['name'] in ['libEGL_impl.so','harmony-mesa/gbm/dri_gbm.so'] or (row['name'].startswith('harmony-mesa/') and '/' not in row['name'][len('harmony-mesa/'):])
 add('graphics-egl/'+row['name'],stat.S_IFREG|0o444,p.read_bytes())
""" + anchor)
compile(payload, 'original-graphics-054-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=480).returncode)
