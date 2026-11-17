"""Verify exact OOBE delta, full overlay chain, runtime guards and workflow."""
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
    work, report = BUILD / 'commercial61-native-114', ROOT / 'reports/commercial61-native-114'
    assert not (report / 'admission-test.json').exists()
    parse = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    def members(path):
        data = path.read_bytes()
        raw = lzma.decompress(data) if data.startswith(b'\xfd7zXZ') else gzip.decompress(data)
        return {n: (mode, body) for n, mode, body in parse(raw)}
    before, after = members(BUILD / 'commercial61-native-109/initrd.img'), members(work / 'initrd.img')
    key = 'native-target/harmonymac-reference099.sh'
    assert set(before) == set(after)
    assert {n for n in before if before[n] != after[n]} == {key}
    api = runpy.run_path(str(BASE / 'oobe-single-launch-114.py'))
    assert after[key] == (before[key][0], api['adapt'](before[key][1].decode()).encode())
    for name in ('init', 'bootstrap-runtime087', 'bootstrap'):
        assert (work / name).read_bytes() == (BUILD / 'commercial61-native-109' / name).read_bytes()
    outer = (work / 'init.c').read_text()
    result = json.loads((report / 'result.json').read_text())
    runtime = result['oobe114']
    assert outer.count(runtime['runtime_path']) == 5 and outer.count(runtime['runtime_sha256']) == 2
    assert sha((work / 'bootstrap-runtime087').read_bytes()) == runtime['runtime_sha256']
    assert after['native-target/desktop-order020.sh'] == before['native-target/desktop-order020.sh']
    assert b'/usr/bin/begetctl start_service accountmgr' in after['native-target/desktop-order020.sh'][1]
    assert after[key][1].count(b'/system/bin/aa force-stop ') == 1
    assert b'/system/bin/aa start ' not in after[key][1]
    assert sha(after['native-target/reference-stack-probe103'][1]) == 'bc9f14107ebfb682311bf8c714f148df579141bb443a358ff85199cdc443b181'
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
    tests = runpy.run_path(str(BASE / 'test-oobe-single-launch-114.py'))
    suite = tests['unittest'].defaultTestLoader.loadTestsFromTestCase(tests['SingleLaunch'])
    assert tests['unittest'].TextTestRunner(verbosity=2).run(suite).wasSuccessful()
    guards = []
    with tempfile.TemporaryDirectory(prefix='commercial114-guards-') as directory:
        for name in ('init', 'bootstrap', 'bootstrap-runtime087'):
            executable = Path(directory) / name
            shutil.copyfile(work / name, executable)
            executable.chmod(0o755)
            run = subprocess.run(['qemu-aarch64', str(executable)], capture_output=True, timeout=15)
            assert run.returncode == 77, (name, run.returncode)
            guards.append(dict(name=name, status=77))
    workflow = runpy.run_path(str(BASE / 'commercial-workflow-114.py'))
    for operation in workflow['OPERATIONS']:
        source = workflow['source114'](operation)
        compile(source, operation, 'exec')
        assert 'StrictHostKeyChecking=yes' in source
        if operation == 'install-commercial-native':
            assert repr(runtime['runtime_path'].removeprefix('/mnt/ubuntu')) in source
            assert "'initrd /commercial61-native-109/initrd.img','initrd /commercial61-native-114/initrd.img',options" in source
            assert '32*1024**2' in source and 'entry.stat().st_size<cluster' in source
        elif operation == 'run-commercial-native':
            assert 'attempt_count=1' in source and '660' in source
        elif operation == 'retrieve-commercial-evidence':
            assert 'ro,noload,nodev,nosuid,noexec' in source
            assert 'commercial61-native-087-8c690eb5-863b-48c3-a0a9-6c123e8b06c2' in source
            assert 'original UDID found; refusing export' in source
        else:
            assert 'commercial_original_images_unchanged=verified' in source
            assert 'user_authorized_old_entries_removed=removed_entries' in source
        (report / (operation + '.generated.py')).open('x').write(source)
    admission = dict(exact_single_script_delta=True, early_account_home_bridge_unchanged=True,
        original_services_tokens_identity_and_recovery_unchanged=True, six_script_tests_pass=True,
        three_isolation_guards_pass=True, actual_runtime_path_hash_verified=True,
        full_ordered_overlay_chain_verified=True, bounded_one_boot_and_preservation_gates_retained=True)
    (report / 'guard-tests.json').open('x').write(json.dumps(guards, indent=2))
    (report / 'admission-test.json').open('x').write(json.dumps(admission, indent=2))
    print(json.dumps(admission, indent=2))
