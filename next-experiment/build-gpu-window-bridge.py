"""Build an isolated reference NativeWindow bridge; not a system installation.

Run under WSL Debian Python. The unchanged reference remains read-only.
"""
from pathlib import Path
import shutil
import subprocess

root = Path('/home/zoinve/harmony-virgl-883')
reference = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports')
local = Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
out = root / 'window-bridge'
out.mkdir(exist_ok=False)
platform = out / 'platform-root/system/lib64'
platform.mkdir(parents=True)
shutil.copy2(local / 'gpu-runtime-883/original-platform-libcxx.so', platform / 'libc++.so')
subprocess.run(['python3', str(reference / 'tools/prepare-ohos-toolchain.py'),
                str(root / 'sdk/native'), str(out / 'toolchain'),
                '--prefix', str(root / 'prefix'), '--platform-root', str(out / 'platform-root')], check=True)
shutil.copytree(reference / 'graphics/include', out / 'include')
shutil.copy2(reference / 'graphics/drm_device.c', out / 'drm_device.c')
source = (reference / 'graphics/egl_window_bridge.cpp').read_text()
assert source.count('/system/lib64/aurora-mesa/libEGL.so.1') == 1
(out / 'egl_window_bridge.cpp').write_text(source.replace('/system/lib64/aurora-mesa/', '/system/lib64/lab-virgl883/'))
prefix = root / 'prefix/system'
include = ['-I' + str(out / 'include'), '-I' + str(prefix / 'include'), '-I' + str(prefix / 'include/libdrm')]
subprocess.run([str(out / 'toolchain/ohos-cc'), '-fPIC', '-O2', '-Wall', '-Wextra', '-Werror',
                *include, '-c', str(out / 'drm_device.c'), '-o', str(out / 'drm_device.o')], check=True)
with (out / 'build.log').open('w') as log:
    subprocess.run([str(out / 'toolchain/ohos-platform-cxx'), '-shared', '-fPIC', '-O2', '-std=c++17',
                    '-Wall', '-Wextra', '-DEGL_EGLEXT_PROTOTYPES', *include,
                    str(out / 'egl_window_bridge.cpp'), str(out / 'drm_device.o'),
                    '-L' + str(prefix / 'lib64/lab-virgl883'), '-lGLESv2', '-lgbm', '-ldrm', '-ldl',
                    '-Wl,--no-undefined,-soname,libEGL_impl.so', '-Wl,-Bsymbolic-functions',
                    '-Wl,-rpath,/system/lib64/lab-virgl883', '-o', str(out / 'libEGL_impl.so')],
                   stdout=log, stderr=subprocess.STDOUT, check=True)
print(subprocess.check_output(['readelf', '-dW', str(out / 'libEGL_impl.so')], text=True))
print('BUILD ONLY: NativeWindow integration and desktop not yet tested')
