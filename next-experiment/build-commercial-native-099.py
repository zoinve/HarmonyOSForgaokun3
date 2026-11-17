"""Reproduce the reference service-first ordering on the genuine identity stack."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import shutil
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')
REFERENCE = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816')


def sha(body):
    return hashlib.sha256(body).hexdigest()


def reference_script():
    revision = subprocess.check_output(['git', '-C', str(REFERENCE), 'rev-parse', 'HEAD'], text=True).strip()
    assert revision == 'f23a5d73f86ef0e45d3e7ac879a0605049a3c9ad'
    checkout = (REFERENCE/'ports/tests/native-desktop-start.sh').read_bytes()
    tracked = subprocess.check_output(['git', '-C', str(REFERENCE), 'show', 'HEAD:ports/tests/native-desktop-start.sh'])
    assert checkout.replace(b'\r\n', b'\n') == tracked, 'Reference checkout differs beyond Windows line endings'
    original = tracked
    anchor = b'exec >/data/boot/aurora/native-desktop.log 2>&1'
    assert original.count(anchor) == 1
    return original, original.replace(anchor, b'exec >/data/commercial-direct-desktop075.log 2>&1', 1)


def main():
    work, report = BUILD/'commercial61-native-099', ROOT/'reports/commercial61-native-099'
    assert not work.exists() and not report.exists()
    tests = json.loads((ROOT/'reports/reference-order-099-tests.json').read_text())
    original, script = reference_script()
    observer = (BASE/'commercial-reference-observer-099.sh').read_bytes()
    assert tests['reference_sha256'] == sha(original)
    assert tests['adapted_sha256'] == sha(script)
    assert tests['observer_sha256'] == sha(observer)
    assert tests['all_scenarios_passed'] is True
    parse = runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    pack = runpy.run_path(str(BASE/'build-commercial-native-087.py'))['member']
    before = {n: (m, d) for n, m, d in parse(gzip.decompress((BUILD/'commercial61-native-095/initrd.img').read_bytes()))}
    after = dict(before)
    key = 'native-target/commercial-desktop077.sh'
    anchor = b'/system/bin/sh /commercial-normal-close095.sh &\n'
    assert before[key][1].count(anchor) == 1
    after[key] = (before[key][0], before[key][1].replace(anchor,
        b'/system/bin/sh /commercial-reference-observer099.sh &\n', 1).replace(
        b'REFRESH090_BEGIN real_wpa_cycle_once=1 no_guide_stop=1 provisioning_unchanged=1',
        b'REFERENCE099_BEGIN real_wpa_cycle_once=1 reference_stop_once=1 provisioning_unchanged=1', 1))
    additions = {'native-target/harmonymac-reference099.sh': (0o100755, script),
                 'native-target/commercial-reference-observer099.sh': (0o100755, observer)}
    assert not set(additions).intersection(before)
    after.update(additions)
    work.mkdir()
    report.mkdir()
    previous = json.loads((ROOT/'reports/commercial61-native-095/result.json').read_text())
    names = [i['name'] for i in previous['artifacts']]
    for item in previous['artifacts']:
        if item['name'] == 'initrd.img':
            continue
        body = (BUILD/'commercial61-native-095'/item['name']).read_bytes()
        assert sha(body) == item['sha256']
        (work/item['name']).open('xb').write(body)
    raw = b''.join(pack(n, m, d, i+1) for i, (n, (m, d)) in enumerate(after.items()))
    raw += pack('TRAILER!!!', 0, b'', len(after)+1)
    (work/'initrd.img').open('xb').write(gzip.compress(raw, compresslevel=6, mtime=0))
    previous['artifacts'] = [dict(name=n, bytes=(work/n).stat().st_size, sha256=sha((work/n).read_bytes())) for n in names]
    previous['reference_order099'] = dict(reference_commit='f23a5d73f86ef0e45d3e7ac879a0605049a3c9ad',
        reference_sha256=sha(original), adapted_sha256=sha(script), observer_sha256=sha(observer),
        sole_reference_change='export log destination', original_startup_order_preserved=True,
        no_guide_or_dock_gate_before_scene_start=True, force_stop_calls=1,
        alt_f4_worker_not_launched=True, identity_network_and_original_cores_unchanged=True,
        original_lifecycle_callbacks_unchanged=True, acceptance_still_unproven=True)
    previous['runtime_verified'] = False
    previous['normal_window_close_diagnostic']['enabled_in_099'] = False
    for folder in (work, report):
        (folder/'result.json').open('x').write(json.dumps(previous, indent=2))
    (report/'reference-original.sh').open('xb').write(original)
    (report/'reference-adapted.sh').open('xb').write(script)
    (report/'observer099.sh').open('xb').write(observer)
    (report/'diagnostic099.sh').open('xb').write(after[key][1])
    shutil.copyfile(ROOT/'reports/commercial61-native-095/config-provenance.json', report/'config-provenance.json')
    print(json.dumps(previous['reference_order099'], indent=2))


if __name__ == '__main__':
    main()
