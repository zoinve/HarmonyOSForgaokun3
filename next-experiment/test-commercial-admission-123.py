"""Check the prepared seed loader, inherited runtime, overlays and boot gates."""
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
    work, report = BUILD / 'commercial61-native-123', ROOT / 'reports/commercial61-native-123'
    assert not (report / 'admission-test.json').exists()
    parse = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    def members(path):
        data = path.read_bytes()
        raw = lzma.decompress(data) if data.startswith(b'\xfd7zXZ') else gzip.decompress(data)
        return {n: (mode, body) for n, mode, body in parse(raw)}
    parent = BUILD / 'commercial61-native-121'
    before, after = members(parent / 'initrd.img'), members(work / 'initrd.img')
    assert set(before) == set(after)
    assert {n for n in before if before[n] != after[n]} == {'init', 'early-hardware093.sh'}
    seed = json.loads((ROOT / 'reports/oobe-seed-preparation-123/result.json').read_text())
    adapt = runpy.run_path(str(BASE / 'build-commercial-native-123.py'))['adapt']
    outer = (work / 'init.c').read_text()
    assert outer == adapt((BUILD / 'commercial61-native-116/init.c').read_text(), seed)
    assert outer.count(seed['seed_sha256']) == 2 and 'oobe_snapshot121' not in outer
    assert outer.index('oobe-seed-load123') < outer.index('int ram=open("/native-target/scratch-data.ext4"')
    for name in ('bootstrap-runtime087', 'bootstrap', 'bootstrap-runtime087.c', 'bootstrap.c'):
        assert (work / name).read_bytes() == (parent / name).read_bytes()
    metadata = json.loads((report / 'result.json').read_text())
    for item in metadata['artifacts']:
        assert sha((work / item['name']).read_bytes()) == item['sha256']
    assert metadata['oobe123']['setup_flags_user_authorized']
    assert not metadata['oobe123']['commercial_activation_modified']
    assert not metadata['oobe123']['sceneboard_cache_copied']
    assert before['native-target/harmonymac-reference099.sh'] == after['native-target/harmonymac-reference099.sh']
    overlay = json.loads((report / 'overlay-result.json').read_text())
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
    tests = subprocess.run(['python3', str(BASE / 'test-oobe-seed-123.py'), '-v'], capture_output=True)
    (report / 'seed-tests.stdout').open('xb').write(tests.stdout)
    (report / 'seed-tests.stderr').open('xb').write(tests.stderr)
    assert tests.returncode == 0 and b'Ran 3 tests' in tests.stderr
    guards = []
    with tempfile.TemporaryDirectory(prefix='oobe123-guards-') as folder:
        for name in ('init', 'bootstrap', 'bootstrap-runtime087'):
            executable = Path(folder) / name
            shutil.copyfile(work / name, executable)
            executable.chmod(0o755)
            test = subprocess.run(['qemu-aarch64', str(executable)], capture_output=True, timeout=15)
            assert test.returncode == 77, (name, test.returncode)
            guards.append(dict(name=name, status=77))
    workflow = runpy.run_path(str(BASE / 'commercial-workflow-123.py'))
    for operation in workflow['OPERATIONS']:
        source = workflow['source123'](operation)
        compile(source, operation, 'exec')
        assert 'StrictHostKeyChecking=yes' in source
        if operation == 'install-commercial-native':
            assert "'initrd /commercial61-native-121/initrd.img','initrd /commercial61-native-123/initrd.img',options" in source
            assert repr(seed['seed_path']) in source and repr(seed['seed_sha256']) in source
            assert '32*1024**2' in source and 'entry.stat().st_size<cluster' in source
        elif operation == 'run-commercial-native':
            assert 'attempt_count=1' in source and '660' in source
        elif operation == 'retrieve-commercial-evidence':
            assert 'ro,noload,nodev,nosuid,noexec' in source and 'unexpected subdirectory' in source
            assert 'commercial61-native-087-5af63052-1886-4135-a836-921af0f8f54d' in source
        else:
            assert 'commercial_original_images_unchanged=verified' in source
            assert 'user_authorized_old_entries_removed=removed_entries' in source
        (report / (operation + '.generated.py')).open('x').write(source)
    result = dict(exact_seed_only_delta_from_116=True, real_original_schema_and_wal_backup_used=True,
        only_two_setup_flags_user_authorized=True, original_runtime_and_services_unchanged=True,
        original_reference_stop_and_recovery_unchanged=True, no_sceneboard_cache_in_seed=True,
        metadata_and_unrelated_rows_preserved=True, three_seed_tests_pass=True,
        three_isolation_guards_pass=True, full_ordered_overlay_chain_verified=True,
        private_seed_hash_required_at_install_and_boot=True, bounded_boot_and_preservation_gates_retained=True)
    (report / 'guard-tests.json').open('x').write(json.dumps(guards, indent=2))
    (report / 'admission-test.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
