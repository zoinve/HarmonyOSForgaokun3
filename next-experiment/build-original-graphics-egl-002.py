"""Keep Mesa's NDK runtime private; never replace the platform std::__h runtime."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('build-original-graphics-egl-001.py')))['payload']
payload = payload.replace('original-graphics-egl-001', 'original-graphics-egl-002')
anchor = "'libz.so.1','libzstd.so.1','liblzma.so.5','libelf.so.1'}"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, "'libz.so.1','libzstd.so.1','liblzma.so.5','libelf.so.1','libc++_shared.so'}")
anchor = "external_original_sdk_dependencies=sorted(external),runtime_executed=False,"
assert payload.count(anchor) == 1
payload = payload.replace(anchor,
    "external_original_sdk_dependencies=sorted(external),runtime_executed=False,\n"
    " legacy_mesa_runpath_alias='/system/lib64/lab-softpipe-167 -> harmony-mesa',\n"
    " mesa_ndk_runtime_scoped=True,platform_libcxx_replaced=False,")
compile(payload, 'original-graphics-egl-002', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=240).returncode)
