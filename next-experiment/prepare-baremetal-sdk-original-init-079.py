"""Use only the original hilog tail command; -x and -z are mutually exclusive."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-078.py')))
source = parent['source'].replace('ORIGINAL_INIT078_', 'ORIGINAL_INIT079_').replace('GRAPHICS078_', 'GRAPHICS079_')
old = '"/system/bin/hilog", "-x", "-z", "200", "-P", argument, NULL'
assert source.count(old) == 1
source = source.replace(old, '"/system/bin/hilog", "-z", "200", "-P", argument, NULL')
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-078', 'baremetal-sdk-original-init-079')
compile(payload, 'original-foundation-tail-079-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
