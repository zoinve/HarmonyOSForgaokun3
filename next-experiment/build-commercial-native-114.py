"""Build a one-variable OOBE comparison; retain the early account/Home bridge."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'next-experiment'
BUILD = Path('/home/zoinve/harmony-virgl-883')


def sha(data):
    return hashlib.sha256(data).hexdigest()


if __name__ == '__main__':
    work = BUILD / 'commercial61-native-114'
    report = ROOT / 'reports/commercial61-native-114'
    assert not work.exists() and not report.exists()
    tests = json.loads((ROOT / 'reports/oobe-single-launch-114/result.json').read_text())
    assert tests['all_passed'] and tests['tests_run'] == 6
    parent = BUILD / 'commercial61-native-109'
    metadata = json.loads((ROOT / 'reports/commercial61-native-109/result.json').read_text())
    for item in metadata['artifacts']:
        assert sha((parent / item['name']).read_bytes()) == item['sha256'], item['name']
    parse = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    pack = runpy.run_path(str(BASE / 'build-commercial-native-087.py'))['member']
    before = {n: (mode, data) for n, mode, data in parse(gzip.decompress((parent / 'initrd.img').read_bytes()))}
    after = dict(before)
    name = 'native-target/harmonymac-reference099.sh'
    original = before[name][1].decode()
    ref = (ROOT / 'reports/commercial61-native-099/reference-original.sh').read_text()
    assert sha(ref.encode()) == tests['reference_sha256']
    assert original == ref.replace('/data/boot/aurora/native-desktop.log', '/data/commercial-direct-desktop075.log', 1)
    adapt = runpy.run_path(str(BASE / 'oobe-single-launch-114.py'))['adapt']
    after[name] = (before[name][0], adapt(original).encode())
    bridge = 'native-target/desktop-order020.sh'
    assert b'/usr/bin/aa start -b com.ohos.sceneboard' in before[bridge][1]
    assert b'/usr/bin/begetctl start_service accountmgr' in before[bridge][1]
    delta = {n: value for n, value in after.items() if value != before.get(n)}
    assert set(delta) == {name}
    assert after[bridge] == before[bridge]
    work.mkdir()
    report.mkdir()
    def archive(entries):
        body = b''.join(pack(n, mode, data, i + 1) for i, (n, (mode, data)) in enumerate(entries.items()))
        return gzip.compress(body + pack('TRAILER!!!', 0, b'', len(entries) + 1), compresslevel=6, mtime=0)
    for item in metadata['artifacts']:
        if item['name'] != 'initrd.img':
            (work / item['name']).open('xb').write((parent / item['name']).read_bytes())
    (work / 'initrd.img').open('xb').write(archive(after))
    overlay = archive(delta)
    (work / 'minimal-overlay.img').open('xb').write(overlay)
    reconstructed = dict(before)
    reconstructed.update({n: (mode, data) for n, mode, data in parse(gzip.decompress(overlay))})
    assert reconstructed == after
    previous = json.loads((ROOT / 'reports/commercial61-native-109/overlay-result.json').read_text())
    overlay_result = dict(bytes=len(overlay), sha256=sha(overlay), members=sorted(delta),
        chain=previous['chain'] + ['commercial61-native-114/initrd.img'],
        shared_parent_overlay_sha256=previous['sha256'], ordered_chain_equals_full_114=True,
        existing_016_overlay_sha256=previous['existing_016_overlay_sha256'],
        original_images_written=False, runtime_verified=False)
    metadata['artifacts'] = [dict(name=item['name'], bytes=(work / item['name']).stat().st_size,
        sha256=sha((work / item['name']).read_bytes())) for item in metadata['artifacts']]
    metadata['oobe114'] = dict(parent='commercial61-native-109', changed_members=sorted(delta),
        early_account_home_bridge_sha256=sha(before[bridge][1]),
        early_bridge_byte_identical=True, runtime_byte_identical_to_109=True,
        runtime_path=metadata['memstack109']['runtime_path'],
        runtime_sha256=metadata['memstack109']['runtime_sha256'],
        second_scene_start_removed=True, original_recovery_unchanged=True,
        single_reference_force_stop_retained=True, duplicate_start_causality_unproven=True,
        installed=False, target_boot_performed=False)
    metadata['runtime_verified'] = False
    for directory in (work, report):
        (directory / 'result.json').open('x').write(json.dumps(metadata, indent=2))
        (directory / 'overlay-result.json').open('x').write(json.dumps(overlay_result, indent=2))
    (report / 'reference-adapted.sh').open('xb').write(after[name][1])
    print(json.dumps(metadata['oobe114'], indent=2))
