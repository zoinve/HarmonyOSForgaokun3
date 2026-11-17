"""Gate early Home on an original collaboration checkpoint, parent 114."""
from pathlib import Path
import gzip
import hashlib
import json
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')


def sha(data):
    return hashlib.sha256(data).hexdigest()


if __name__ == '__main__':
    work, report = BUILD / 'commercial61-native-116', ROOT / 'reports/commercial61-native-116'
    assert not work.exists() and not report.exists()
    order = json.loads((ROOT / 'reports/oobe-query-order-115.json').read_text())
    assert order['replacement_query_duration_ms'] == 7
    parent = BUILD / 'commercial61-native-114'
    metadata = json.loads((ROOT / 'reports/commercial61-native-114/result.json').read_text())
    for item in metadata['artifacts']:
        assert sha((parent / item['name']).read_bytes()) == item['sha256']
    parse = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    pack = runpy.run_path(str(BASE / 'build-commercial-native-087.py'))['member']
    before = {n: (mode, data) for n, mode, data in parse(gzip.decompress((parent / 'initrd.img').read_bytes()))}
    after = dict(before)
    bridge = 'native-target/desktop-order020.sh'
    adapt = runpy.run_path(str(BASE / 'oobe-startup-gate-116.py'))['adapt']
    after[bridge] = (before[bridge][0], adapt(before[bridge][1].decode()).encode())
    helper = 'native-target/commercial-collaboration-ready116.sh'
    assert helper not in before
    after[helper] = (0o100755, (BASE / 'commercial-collaboration-ready-116.sh').read_bytes())
    outer = (parent / 'init.c').read_text()
    anchor = '"commercial-memmgr-stack109.log"'
    assert outer.count(anchor) == 1
    outer = outer.replace(anchor, anchor + ',"commercial-collaboration-ready116.log"', 1)
    work.mkdir()
    report.mkdir()
    tests = subprocess.run(['python3', str(BASE / 'test-oobe-startup-gate-116.py'), '-v'], capture_output=True)
    (report / 'gate-tests.stdout').open('xb').write(tests.stdout)
    (report / 'gate-tests.stderr').open('xb').write(tests.stderr)
    assert tests.returncode == 0 and b'Ran 8 tests' in tests.stderr
    for item in metadata['artifacts']:
        if item['name'] not in ('init', 'init.c', 'initrd.img'):
            (work / item['name']).open('xb').write((parent / item['name']).read_bytes())
    (work / 'init.c').open('x').write(outer)
    compile_result = subprocess.run(['aarch64-linux-gnu-gcc', '-static', '-O2', '-Wall', '-Wextra', '-Werror',
        str(work / 'init.c'), '-I', str(BASE), str(BASE / 'baremetal-diagnostic-core.c'), '-o', str(work / 'init')],
        capture_output=True)
    (report / 'init.stdout').open('xb').write(compile_result.stdout)
    (report / 'init.stderr').open('xb').write(compile_result.stderr)
    assert compile_result.returncode == 0, compile_result.stderr.decode(errors='replace')
    after['init'] = (before['init'][0], (work / 'init').read_bytes())
    wrapper = before['early-hardware093.sh'][1]
    assert wrapper.count(sha(before['init'][1]).encode()) == 1
    after['early-hardware093.sh'] = (before['early-hardware093.sh'][0],
        wrapper.replace(sha(before['init'][1]).encode(), sha(after['init'][1]).encode(), 1))
    delta = {n: value for n, value in after.items() if value != before.get(n)}
    assert set(delta) == {'init', 'early-hardware093.sh', bridge, helper}
    def archive(entries):
        raw = b''.join(pack(n, mode, data, i + 1) for i, (n, (mode, data)) in enumerate(entries.items()))
        return gzip.compress(raw + pack('TRAILER!!!', 0, b'', len(entries) + 1), compresslevel=6, mtime=0)
    (work / 'initrd.img').open('xb').write(archive(after))
    overlay = archive(delta)
    (work / 'minimal-overlay.img').open('xb').write(overlay)
    reconstructed = dict(before)
    reconstructed.update({n: (mode, data) for n, mode, data in parse(gzip.decompress(overlay))})
    assert reconstructed == after
    previous = json.loads((ROOT / 'reports/commercial61-native-114/overlay-result.json').read_text())
    overlay_result = dict(bytes=len(overlay), sha256=sha(overlay), members=sorted(delta),
        chain=previous['chain'] + ['commercial61-native-116/initrd.img'],
        shared_parent_overlay_sha256=previous['sha256'], ordered_chain_equals_full_116=True,
        existing_016_overlay_sha256=previous['existing_016_overlay_sha256'],
        original_images_written=False, runtime_verified=False)
    metadata['artifacts'] = [dict(name=item['name'], bytes=(work / item['name']).stat().st_size,
        sha256=sha((work / item['name']).read_bytes())) for item in metadata['artifacts']]
    metadata['oobe116'] = dict(parent='commercial61-native-114', changed_members=sorted(delta),
        runtime_path=metadata['oobe114']['runtime_path'], runtime_sha256=metadata['oobe114']['runtime_sha256'],
        runtime_byte_identical_to_114=True, original_services_and_callbacks_unchanged=True,
        original_checkpoint_is_not_full_service_readiness=True, checkpoint_dependency_may_deadlock_until_timeout=True,
        early_home_gate_added=True, eight_gate_tests_pass=True,
        single_reference_force_stop_unchanged=True, installed=False, target_boot_performed=False)
    metadata['runtime_verified'] = False
    for directory in (work, report):
        (directory / 'result.json').open('x').write(json.dumps(metadata, indent=2))
        (directory / 'overlay-result.json').open('x').write(json.dumps(overlay_result, indent=2))
    (report / 'gate116.sh').open('xb').write(after[helper][1])
    (report / 'desktop-order020.sh').open('xb').write(after[bridge][1])
    print(json.dumps(metadata['oobe116'], indent=2))
