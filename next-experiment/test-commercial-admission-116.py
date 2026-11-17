"""Validate original checkpoint gate, log exporter, overlays and boot guards."""
from pathlib import Path
import gzip
import hashlib
import json
import lzma
import runpy
import shutil
import subprocess
import tempfile

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
BUILD = Path('/home/zoinve/harmony-virgl-883')


def sha(data):
    return hashlib.sha256(data).hexdigest()


if __name__ == '__main__':
    work, report = BUILD / 'commercial61-native-116', ROOT / 'reports/commercial61-native-116'
    assert not (report / 'admission-test.json').exists()
    parse = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    def members(path):
        data = path.read_bytes()
        raw = lzma.decompress(data) if data.startswith(b'\xfd7zXZ') else gzip.decompress(data)
        return {n: (mode, body) for n, mode, body in parse(raw)}
    before, after = members(BUILD / 'commercial61-native-114/initrd.img'), members(work / 'initrd.img')
    bridge = 'native-target/desktop-order020.sh'
    helper = 'native-target/commercial-collaboration-ready116.sh'
    assert set(after) - set(before) == {helper}
    assert {n for n in before if before[n] != after[n]} == {'init', 'early-hardware093.sh', bridge}
    api = runpy.run_path(str(BASE / 'oobe-startup-gate-116.py'))
    assert after[bridge] == (before[bridge][0], api['adapt'](before[bridge][1].decode()).encode())
    assert after[helper] == (0o100755, (BASE / 'commercial-collaboration-ready-116.sh').read_bytes())
    assert after['native-target/harmonymac-reference099.sh'] == before['native-target/harmonymac-reference099.sh']
    assert after['native-target/harmonymac-reference099.sh'][1].count(b'/system/bin/aa force-stop ') == 1
    parent = BUILD / 'commercial61-native-114'
    for name in ('bootstrap-runtime087', 'bootstrap', 'bootstrap-runtime087.c', 'bootstrap.c'):
        assert (work / name).read_bytes() == (parent / name).read_bytes()
    outer = (work / 'init.c').read_text()
    expected = (parent / 'init.c').read_text().replace('"commercial-memmgr-stack109.log"',
        '"commercial-memmgr-stack109.log","commercial-collaboration-ready116.log"', 1)
    assert outer == expected and outer.count('"commercial-collaboration-ready116.log"') == 1
    assert after['early-hardware093.sh'][1] == before['early-hardware093.sh'][1].replace(
        sha(before['init'][1]).encode(), sha(after['init'][1]).encode(), 1)
    result = json.loads((report / 'result.json').read_text())
    runtime = result['oobe116']
    assert outer.count(runtime['runtime_path']) == 5 and outer.count(runtime['runtime_sha256']) == 2
    assert sha((work / 'bootstrap-runtime087').read_bytes()) == runtime['runtime_sha256']
    for item in result['artifacts']:
        assert sha((work / item['name']).read_bytes()) == item['sha256']
    overlay = json.loads((report / 'overlay-result.json').read_text())
    assert sha((work / 'minimal-overlay.img').read_bytes()) == overlay['sha256']
    merged = {}
    for relative in overlay['chain']:
        number, filename = relative.split('/')
        if filename == 'early094.img':
            path = BUILD / 'commercial61-native-094/minimal-overlay.img'
        elif number == 'commercial61-native-001':
            path = BUILD / number / filename
        elif number == 'commercial61-native-016':
            path = BUILD / 'commercial61-native-016-r2/minimal-overlay.img'
        elif number == 'commercial61-native-072':
            path = BUILD / number / 'minimal-overlay-xz.img'
        else:
            path = BUILD / number / 'minimal-overlay.img'
        merged.update(members(path))
    assert merged == after
    assert b'Ran 8 tests' in (report / 'gate-tests.stderr').read_bytes()
    guards = []
    with tempfile.TemporaryDirectory(prefix='commercial116-guards-') as directory:
        for name in ('init', 'bootstrap', 'bootstrap-runtime087'):
            executable = Path(directory) / name
            shutil.copyfile(work / name, executable)
            executable.chmod(0o755)
            run = subprocess.run(['qemu-aarch64', str(executable)], capture_output=True, timeout=15)
            assert run.returncode == 77, (name, run.returncode)
            guards.append(dict(name=name, status=77))
    workflow = runpy.run_path(str(BASE / 'commercial-workflow-116.py'))
    for operation in workflow['OPERATIONS']:
        source = workflow['source116'](operation)
        compile(source, operation, 'exec')
        assert 'StrictHostKeyChecking=yes' in source
        if operation == 'install-commercial-native':
            assert repr(runtime['runtime_path'].removeprefix('/mnt/ubuntu')) in source
            assert "'initrd /commercial61-native-114/initrd.img','initrd /commercial61-native-116/initrd.img',options" in source
            assert '32*1024**2' in source and 'entry.stat().st_size<cluster' in source
        elif operation == 'run-commercial-native':
            assert 'attempt_count=1' in source and '660' in source
        elif operation == 'retrieve-commercial-evidence':
            assert 'ro,noload,nodev,nosuid,noexec' in source
            assert 'commercial61-native-087-34528a49-dbee-4569-86d7-5379123af688' in source
            assert 'original UDID found; refusing export' in source
        else:
            assert 'commercial_original_images_unchanged=verified' in source
            assert 'user_authorized_old_entries_removed=removed_entries' in source
        (report / (operation + '.generated.py')).open('x').write(source)
    admission = dict(exact_gate_and_exporter_delta=True, original_reference_stop_script_unchanged=True,
        original_services_tokens_identity_and_recovery_unchanged=True, eight_gate_tests_pass=True,
        three_isolation_guards_pass=True, actual_runtime_path_hash_verified=True,
        full_ordered_overlay_chain_verified=True, bounded_one_boot_and_preservation_gates_retained=True)
    (report / 'guard-tests.json').open('x').write(json.dumps(guards, indent=2))
    (report / 'admission-test.json').open('x').write(json.dumps(admission, indent=2))
    print(json.dumps(admission, indent=2))
