"""Passively capture bounded full-composer traces beside unchanged EGL traces."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-068.py')))
source = parent['source'].replace('ORIGINAL_INIT068_', 'ORIGINAL_INIT069_').replace('GRAPHICS068_', 'GRAPHICS069_')
anchor = 'if (strncmp(entry->d_name, "egl-", 4) || strchr(entry->d_name, \'/\')) continue;'
assert source.count(anchor) == 1
source = source.replace(anchor, 'if ((strncmp(entry->d_name, "egl-", 4) && strncmp(entry->d_name, "composer-", 9)) || strchr(entry->d_name, \'/\')) continue;')
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-068', 'baremetal-sdk-original-init-069')
compile(payload, 'original-graphics-069-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
