"""Exact completed-experiment userdata cleanup, with original-image guards."""
from pathlib import Path
import hashlib
import json
import os

lab = Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab')
old = lab / 'official-arm-sdk-921/full-system-923'
target = old / 'userdata-permissive.img'
report = old / 'userdata-cleanup.json'
assert not report.exists()
result = json.loads((old / 'result.json').read_text())
assert all(result[k] for k in ('readonly_inputs_unchanged', 'official_originals_unchanged', 'protected_userdata_original_unchanged'))
evidence = old / 'readonly-cppcrash-1248-1794385026239.json'
assert json.loads(evidence.read_text())['PNAME'] == '/system/bin/render_service'

def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

config = json.loads((old / 'config.json').read_text())
protected = lab / 'disks-744/userdata-analysis.img'
expected = '667cbbb0658558eb2a80d13f61f5bbc6ce54e4bbd8f5c0a6817e881566ac2f56'
assert sha(protected) == expected
for row in config['originals']:
    assert sha(row['path']) == row['sha256']
assert target.is_file() and not target.is_symlink() and target.stat().st_size == 104857600
for proc in Path('/proc').iterdir():
    if not proc.name.isdigit():
        continue
    try:
        assert 'qemu-system-' not in os.readlink(proc / 'exe')
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        pass
    try:
        for fd in (proc / 'fd').iterdir():
            try:
                assert os.readlink(fd) != str(target)
            except (FileNotFoundError, PermissionError, ProcessLookupError):
                pass
    except (FileNotFoundError, PermissionError, ProcessLookupError):
        pass
target.unlink()
assert sha(protected) == expected
for row in config['originals']:
    assert sha(row['path']) == row['sha256']
data = dict(deleted=str(target), bytes=104857600, original_images_verified_before_after=True,
            crash_evidence_sha256=sha(evidence), evidence_preserved=True)
report.write_text(json.dumps(data, indent=2))
print(json.dumps(data, indent=2))
