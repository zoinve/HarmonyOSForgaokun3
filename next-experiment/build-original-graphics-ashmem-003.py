"""Prepare missing module link inputs in a copy, never the retained kernel build."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('build-original-graphics-ashmem-002.py')))['payload']
payload = payload.replace('original-graphics-ashmem-002', 'original-graphics-ashmem-003')
anchor = "cmd = ['make', '-C', str(k),"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, '''build_k = out / 'kernel-build'
subprocess.run(['cp', '-a', '--reflink=auto', str(k), str(build_k)], check=True)
prepare = subprocess.run(['make', '-C', str(build_k), 'ARCH=arm64', 'CROSS_COMPILE=aarch64-linux-gnu-', 'modules_prepare'], text=True, capture_output=True)
(local / 'prepare.stdout.txt').write_text(prepare.stdout)
(local / 'prepare.stderr.txt').write_text(prepare.stderr)
prepare.check_returncode()
assert (build_k / 'scripts/module.lds').is_file()
# This Image-only kernel has no in-tree modules: its genuine exported vmlinux
# table is the complete kernel symbol input. No unresolved-symbol waiver.
(build_k / 'Module.symvers').write_bytes((k / 'vmlinux.symvers').read_bytes())
cmd = ['make', '-C', str(build_k),''')
extra = "'KBUILD_EXTRA_SYMBOLS=' + str(k / 'vmlinux.symvers'), "
assert payload.count(extra) == 1
payload = payload.replace(extra, '')
compile(payload, 'graphics-ashmem-003-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=300).returncode)
