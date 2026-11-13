"""Explicit source + O= prevents copied Kbuild Makefile redirecting to its origin."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('build-original-graphics-ashmem-003.py')))['payload']
payload = payload.replace('original-graphics-ashmem-003', 'original-graphics-ashmem-004')
old = "'-C', str(build_k),"
assert payload.count(old) == 2
payload = payload.replace(old, "'-C', str(k.parent / 'linux'), 'O=' + str(build_k),")
compile(payload, 'graphics-ashmem-004-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=300).returncode)
