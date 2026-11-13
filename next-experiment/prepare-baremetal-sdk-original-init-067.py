"""Extend passive original-service observation; do not alter the service graph."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-066.py')))
source = parent['source'].replace('ORIGINAL_INIT066_', 'ORIGINAL_INIT067_').replace('GRAPHICS066_', 'GRAPHICS067_')
old = 'for (unsigned sample = 0; sample < 24; ++sample) {'
assert source.count(old) == 1
source = source.replace(old, old.replace('< 24', '< 48'))
old = 'sample == 9 || sample == 13 || sample == 17'
assert source.count(old) == 2
source = source.replace(old, old + ' || sample == 29 || sample == 41')
source = source.replace('if (sample == 15) {', 'if (sample == 15 || sample == 35) {')
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-066', 'baremetal-sdk-original-init-067')
compile(payload, 'original-graphics-067-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
