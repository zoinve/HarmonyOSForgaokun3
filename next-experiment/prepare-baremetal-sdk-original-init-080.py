"""Read early original Foundation records instead of repeating late RDB errors."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-079.py')))
source = parent['source'].replace('ORIGINAL_INIT079_', 'ORIGINAL_INIT080_').replace('GRAPHICS079_', 'GRAPHICS080_')
old = '"/system/bin/hilog", "-z", "200", "-P", argument, NULL'
assert source.count(old) == 1
source = source.replace(old, '"/system/bin/hilog", "-a", "600", "-P", argument, NULL')
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-079', 'baremetal-sdk-original-init-080')
compile(payload, 'original-bms-head-080-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
