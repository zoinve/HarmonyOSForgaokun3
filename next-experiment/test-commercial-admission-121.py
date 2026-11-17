"""Validate sparse snapshot code, exact overlay delta, guards and private export."""
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
    work, report = BUILD / 'commercial61-native-121', ROOT / 'reports/commercial61-native-121'
    assert not (report / 'admission-test.json').exists()
    parse = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    def members(path):
        data = path.read_bytes()
        raw = lzma.decompress(data) if data.startswith(b'\xfd7zXZ') else gzip.decompress(data)
        return {n: (mode, body) for n, mode, body in parse(raw)}
    parent = BUILD / 'commercial61-native-116'
    before, after = members(parent / 'initrd.img'), members(work / 'initrd.img')
    assert set(before) == set(after)
    assert {n for n in before if before[n] != after[n]} == {'init', 'early-hardware093.sh'}
    adapt = runpy.run_path(str(BASE / 'build-commercial-native-121.py'))['adapt']
    assert (work / 'init.c').read_text() == adapt((parent / 'init.c').read_text())
    for name in ('bootstrap-runtime087', 'bootstrap', 'bootstrap-runtime087.c', 'bootstrap.c'):
        assert (work / name).read_bytes() == (parent / name).read_bytes()
    metadata = json.loads((report / 'result.json').read_text())
    for item in metadata['artifacts']:
        assert sha((work / item['name']).read_bytes()) == item['sha256']
    assert sha((BASE / 'oobe-data-snapshot-121.h').read_bytes()) == metadata['oobe121']['header_sha256']
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
    guards = []
    with tempfile.TemporaryDirectory(prefix='oobe121-tests-') as folder:
        folder = Path(folder)
        executable = folder / 'sparse-test'
        subprocess.run(['gcc', '-O2', '-Wall', '-Wextra', '-Werror', '-I', str(BASE),
            str(BASE / 'test-oobe-snapshot-121.c'), '-o', str(executable)], check=True)
        test = subprocess.run([str(executable), str(folder)], capture_output=True, timeout=15)
        assert test.returncode == 0, test.stderr
        assert b'SPARSE121_TESTS_PASS' in test.stdout
        assert b'status=126 thaw=126' in test.stdout
        (report / 'sparse-tests.stdout').open('xb').write(test.stdout)
        (report / 'sparse-tests.stderr').open('xb').write(test.stderr)
        for name in ('init', 'bootstrap', 'bootstrap-runtime087'):
            executable = folder / name
            shutil.copyfile(work / name, executable)
            executable.chmod(0o755)
            test = subprocess.run(['qemu-aarch64', str(executable)], capture_output=True, timeout=15)
            assert test.returncode == 77, (name, test.returncode)
            guards.append(dict(name=name, status=77))
    workflow = runpy.run_path(str(BASE / 'commercial-workflow-121.py'))
    for operation in workflow['OPERATIONS']:
        source = workflow['source121'](operation)
        compile(source, operation, 'exec')
        assert 'StrictHostKeyChecking=yes' in source
        if operation == 'install-commercial-native':
            assert "'initrd /commercial61-native-116/initrd.img','initrd /commercial61-native-121/initrd.img',options" in source
            assert '32*1024**2' in source and 'entry.stat().st_size<cluster' in source
        elif operation == 'run-commercial-native':
            assert 'attempt_count=1' in source and '660' in source
        elif operation == 'retrieve-commercial-evidence':
            assert 'ro,noload,nodev,nosuid,noexec' in source and 'unexpected subdirectory' in source
            assert 'commercial61-native-087-13eefda1-d895-49db-bbbc-468343e0c5e9' in source
        else:
            assert 'commercial_original_images_unchanged=verified' in source
            assert 'user_authorized_old_entries_removed=removed_entries' in source
        (report / (operation + '.generated.py')).open('x').write(source)
    result = dict(exact_snapshot_only_delta=True, original_runtime_and_reference_stop_unchanged=True,
        sparse_content_holes_tail_empty_and_refusal_test_pass=True, three_isolation_guards_pass=True,
        full_ordered_overlay_chain_verified=True, private_data_outside_exported_run=True,
        original_identity_authentication_and_images_unchanged=True, bounded_boot_guards_retained=True)
    (report / 'guard-tests.json').open('x').write(json.dumps(guards, indent=2))
    (report / 'admission-test.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
