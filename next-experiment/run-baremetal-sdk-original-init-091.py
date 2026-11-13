"""Fresh sparse lab-only disk avoids RAM pressure; retain independent copy hashes."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-090.py')))['payload']
for old, new in [('original-init-qemu-090', 'original-init-qemu-091'),
                 ('original-init-090/result.json', 'original-init-091/result.json'),
                 ('harmony-sdk-qemu090-', 'harmony-sdk-qemu091-'),
                 ('GRAPHICS090_', 'GRAPHICS091_'), ('ORIGINAL_INIT090_', 'ORIGINAL_INIT091_')]:
    assert old in payload, old
    payload = payload.replace(old, new)
changes = [
    ("shutil.disk_usage('/dev/shm').free > 768*1024*1024", 'shutil.disk_usage(work).free > 17*1024*1024*1024'),
    ("dir='/dev/shm'", 'dir=str(work)'),
    ('ram_backed=True', 'ram_backed=False,disk_backed=True,test_only=True'),
    ("scratch.parent==Path('/dev/shm')", 'scratch.parent==work'),
]
for old, new in changes:
    assert payload.count(old) == 1, old
    payload = payload.replace(old, new)
assert payload.count('512*1024*1024') == 3
payload = payload.replace('512*1024*1024', '8*1024*1024*1024')
compile(payload, 'original-data-capacity-091-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=660).returncode)
