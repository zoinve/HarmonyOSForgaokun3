"""Independently verify full-graph observations, not graphics readiness."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

BASE = Path(__file__).resolve().parents[1]


def sha(body):
    return hashlib.sha256(body).hexdigest()


def main():
    out = BASE / 'reports/original-graphics-boot-047-independent.json'
    assert not out.exists()
    folder = BASE / 'reports/baremetal-sdk-original-init-qemu-047'
    result = json.loads((folder / 'result.json').read_text())
    raw = (folder / 'serial.log').read_bytes()
    assert sha(raw) == result['serial_sha256'] and len(raw) == result['serial_bytes']
    assert all(result[k] for k in ['original_images_unchanged', 'kernel_and_config_unchanged',
                                   'native_config_unchanged', 'source_critical_unchanged'])
    assert not result['helper_failure_observed'] and result['observation_timed_out']
    modes = re.findall(rb'GRAPHICS047_SELINUX sample=(\d+) enforce=(\d)', raw)
    assert len(modes) == 12 and {v for _, v in modes} == {b'0'}, modes
    rs = re.findall(rb'GRAPHICS047_PROCESS sample=(\d+) pid=(\d+) cmd=/system/bin/render_service', raw)
    assert len(rs) >= 2 and len({pid for _, pid in rs}) == 1
    pid = rs[0][1]
    assert b'GRAPHICS047_IDENTITY pid=' + pid + b' Uid:\t1003\t1003\t1003\t1003' in raw
    assert b'GRAPHICS047_DOMAIN pid=' + pid + b' value=u:r:render_service:s0' in raw
    assert b'/system/lib64/librender_service.z.so' in raw
    assert b'cmd=foundation ' in raw
    assert b'Reset cmd cannot find service composer_host' in raw
    assert b'Reset cmd cannot find service allocator_host' in raw
    collected = BASE / 'reports/baremetal-native-trial-012-collected'
    prior = json.loads((collected / 'collection.json').read_text())['files']
    assert len(prior) == 378
    for row in prior:
        data = (collected / row['path']).read_bytes()
        assert sha(data) == row['sha256'] and len(data) == row['bytes']
    script = '''import hashlib,json
from pathlib import Path
rows=json.loads(%r)
for row in rows.values():
 p=Path(row['path'])
 assert p.stat().st_size==row['bytes']
 with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==row['sha256']
print('ORIGINAL_IMAGES_INDEPENDENT_HASH_PASS')
''' % json.dumps(result['original_images'])
    checked = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=script,
                             text=True, capture_output=True, check=True, timeout=120)
    evidence = dict(serial_sha256=sha(raw), original_images_independent_hashes=True,
                    prior_native_raw_files_verified=len(prior), observed_mode='permissive',
                    mode_samples=len(modes), render_service_pid=int(pid), original_uid=1003,
                    original_domain='u:r:render_service:s0', original_foundation_observed=True,
                    composer_allocator_service_registration_missing=True,
                    guest_observation_timed_out=True, readiness_verified=False,
                    desktop_verified=False, physical_board_test=False,
                    image_hash_stdout=checked.stdout)
    with out.open('x') as f:
        json.dump(evidence, f, indent=2)
    print(json.dumps(evidence, indent=2))


if __name__ == '__main__':
    main()
