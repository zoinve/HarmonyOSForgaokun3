"""Verify actual original host registration and retain the guest critical failure."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

BASE = Path(__file__).resolve().parents[1]


def main():
    out = BASE / 'reports/original-graphics-boot-048-independent.json'
    assert not out.exists()
    folder = BASE / 'reports/baremetal-sdk-original-init-qemu-048'
    result = json.loads((folder / 'result.json').read_text())
    raw = (folder / 'serial.log').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == result['serial_sha256']
    assert len(raw) == result['serial_bytes']
    assert all(result[k] for k in ['original_images_unchanged', 'kernel_and_config_unchanged',
                                   'native_config_unchanged', 'source_critical_unchanged'])
    assert not result['helper_failure_observed']
    assert result['qemu_returncode'] == 0 and not result['observation_timed_out']
    modes = re.findall(rb'GRAPHICS048_SELINUX sample=(\d+) enforce=(\d)', raw)
    assert len(modes) >= 16 and {v for _, v in modes} == {b'0'}
    identities = {}
    for name, uid in [('composer_host', 3036), ('allocator_host', 3041), ('render_service', 1003)]:
        rows = re.findall(rb'GRAPHICS048_PROCESS sample=(\d+) pid=(\d+) cmd=[^\r\n]*' + name.encode(), raw)
        assert rows, name
        pids = sorted({int(pid) for _, pid in rows})
        for pid in pids:
            prefix = b'GRAPHICS048_IDENTITY pid=' + str(pid).encode() + b' Uid:\t'
            expected = b'\t'.join([str(uid).encode()] * 4)
            assert prefix + expected in raw, (name, pid)
            assert ('GRAPHICS048_DOMAIN pid=%d value=u:r:%s:s0' % (pid, name)).encode() in raw
        identities[name] = dict(pids=pids, uid=uid, domain='u:r:' + name + ':s0')
    assert b'GRAPHICS048_VENDOR_IMPORT original_service_config=1 service_credentials_unmodified=1' in raw
    assert b'Reset cmd cannot find service composer_host' not in raw
    assert b'Reset cmd cannot find service allocator_host' not in raw
    assert b'ProcessCriticalProcessFault serviceName is foundation' in raw
    assert b'reboot: Restarting system' in raw
    collected = BASE / 'reports/baremetal-native-trial-012-collected'
    prior = json.loads((collected / 'collection.json').read_text())['files']
    assert len(prior) == 378
    for row in prior:
        body = (collected / row['path']).read_bytes()
        assert len(body) == row['bytes'] and hashlib.sha256(body).hexdigest() == row['sha256']
    script = '''import hashlib,json
from pathlib import Path
for row in json.loads(%r).values():
 p=Path(row['path']);assert p.stat().st_size==row['bytes']
 with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==row['sha256']
print('ORIGINAL_IMAGES_INDEPENDENT_HASH_PASS')
''' % json.dumps(result['original_images'])
    checked = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=script,
                             text=True, capture_output=True, check=True, timeout=120)
    evidence = dict(serial_sha256=result['serial_sha256'], original_images_independent_hashes=True,
                    prior_native_raw_files_verified=len(prior), observed_mode='permissive',
                    mode_samples=len(modes), original_process_identities=identities,
                    original_host_processes_observed=True, services_restarting=True,
                    foundation_critical_fault_observed=True, guest_reboot_observed=True,
                    readiness_verified=False, desktop_verified=False, physical_board_test=False,
                    image_hash_stdout=checked.stdout)
    with out.open('x') as f:
        json.dump(evidence, f, indent=2)
    print(json.dumps(evidence, indent=2))


if __name__ == '__main__':
    main()
