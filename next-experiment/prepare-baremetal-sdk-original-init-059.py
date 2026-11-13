"""Expose the unmodified GBM library's compiled backend path in RAM only."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-056.py')))
source = parent['source'].replace('ORIGINAL_INIT056_', 'ORIGINAL_INIT059_').replace('GRAPHICS056_', 'GRAPHICS059_')
anchor = '    dprintf(1, "GRAPHICS059_EGL '
assert source.count(anchor) == 1
source = source.replace(anchor, '''    if (symlink("harmony-mesa", "/system/lib64/lab-virgl883"))
        fail("RAM-only GBM compiled backend path alias");
    dprintf(1, "GRAPHICS059_GBM_BACKEND_PATH /system/lib64/lab-virgl883/gbm -> harmony-mesa/gbm original_elf_unchanged=1\\n");
''' + anchor)
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-056', 'baremetal-sdk-original-init-059')
compile(payload, 'original-graphics-059-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
