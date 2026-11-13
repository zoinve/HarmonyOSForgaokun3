"""Use retained Image-only build's genuine vmlinux symbol table for modpost."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('build-original-graphics-ashmem-001.py')))['payload']
payload = payload.replace('original-graphics-ashmem-001', 'original-graphics-ashmem-002')
assert payload.count("k / 'Module.symvers'") == 1
payload = payload.replace("k / 'Module.symvers'", "k / 'vmlinux.symvers'")
assert payload.count("'M=' + str(out), 'modules'") == 1
payload = payload.replace("'M=' + str(out), 'modules'", "'M=' + str(out), 'KBUILD_EXTRA_SYMBOLS=' + str(k / 'vmlinux.symvers'), 'modules'")
compile(payload, 'graphics-ashmem-002-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=300).returncode)
