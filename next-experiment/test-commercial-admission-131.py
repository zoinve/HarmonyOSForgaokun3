"""Verify exact module-only delta, runtime preservation and complete boot chain."""
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
REPORT = ROOT / 'reports/commercial61-native-131'


def sha(data):
    return hashlib.sha256(data).hexdigest()


if __name__ == '__main__':
    assert not (REPORT / 'admission-test.json').exists()
    assert not (REPORT / 'deployment-manifest.json').exists()
    work = BUILD / 'commercial61-native-131'
    parent = BUILD / 'commercial61-native-130'
    build = json.loads((REPORT / 'result.json').read_text())
    original = json.loads((ROOT / 'reports/commercial61-native-130/result.json').read_text())
    parse = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    def members(path):
        data = path.read_bytes()
        raw = lzma.decompress(data) if data.startswith(b'\xfd7zXZ') else gzip.decompress(data)
        return {name: (mode, body) for name, mode, body in parse(raw)}
    for row in original['artifacts']:
        assert sha((parent / row['name']).read_bytes()) == row['sha256']
    before, after = members(parent / 'initrd.img'), members(work / 'initrd.img')
    assert set(before) == set(after)
    assert {name for name in before if before[name] != after[name]} == {'init', 'early-hardware093.sh'}
    assert (work / 'init.c').read_text() == runpy.run_path(str(BASE / 'build-commercial-native-131.py'))['adapt']((parent / 'init.c').read_text())
    assert sha(after[build['module_path']][1]) == build['module_sha256']
    for name in ['bootstrap', 'bootstrap.c', 'bootstrap-runtime087', 'bootstrap-runtime087.c']:
        assert (work / name).read_bytes() == (parent / name).read_bytes()
    minimal = members(work / 'minimal-overlay.img')
    assert set(minimal) == {'init', 'early-hardware093.sh'}
    assert sha((work / 'minimal-overlay.img').read_bytes()) == build['overlay_sha256']
    assert all(minimal[name] == after[name] for name in minimal)
    overlay = json.loads((ROOT / 'reports/commercial61-native-130/overlay-result.json').read_text())
    overlay['shared_parent_overlay_sha256'] = overlay['sha256']
    overlay['bytes'] = build['overlay_bytes']
    overlay['sha256'] = build['overlay_sha256']
    overlay['members'] = sorted(minimal)
    overlay['chain'] = [*overlay['chain'], 'commercial61-native-131/initrd.img']
    del overlay['ordered_chain_equals_full_130']
    merged = {}
    for relative in overlay['chain']:
        number, filename = relative.split('/')
        if filename == 'early094.img':
            path = BUILD / 'commercial61-native-094/minimal-overlay.img'
        elif number == 'commercial61-native-001':
            path = BUILD / relative
        elif number == 'commercial61-native-016':
            path = BUILD / 'commercial61-native-016-r2/minimal-overlay.img'
        elif number == 'commercial61-native-072':
            path = BUILD / number / 'minimal-overlay-xz.img'
        else:
            path = BUILD / number / 'minimal-overlay.img'
        merged.update(members(path))
    assert merged == after
    overlay['ordered_chain_equals_full_131'] = True
    (REPORT / 'overlay-result.json').open('x').write(json.dumps(overlay, indent=2))
    original['artifacts'] = [dict(name=row['name'], bytes=(work / row['name']).stat().st_size,
                                  sha256=sha((work / row['name']).read_bytes())) for row in original['artifacts']]
    original['driver131'] = build
    original['runtime_verified'] = False
    (REPORT / 'deployment-manifest.json').open('x').write(json.dumps(original, indent=2))
    for test in ['test-commercial-battery-131.py', 'test-gaokun-basic-sysfs-001.py',
                 'test-native-backlight-129.py', 'test-oobe-seed-123.py']:
        result = subprocess.run(['python3', str(BASE / test), '-v'], capture_output=True)
        (REPORT / (test + '.stdout')).open('xb').write(result.stdout)
        (REPORT / (test + '.stderr')).open('xb').write(result.stderr)
        assert result.returncode == 0, result.stderr.decode(errors='replace')
    with tempfile.TemporaryDirectory(prefix='driver131-guard-') as directory:
        for name in ['init', 'bootstrap', 'bootstrap-runtime087']:
            binary = Path(directory) / name
            shutil.copyfile(work / name, binary)
            binary.chmod(0o755)
            result = subprocess.run(['qemu-aarch64', str(binary)], capture_output=True, timeout=15)
            assert result.returncode == 77, (name, result.returncode, result.stderr)
    workflow = runpy.run_path(str(BASE / 'commercial-workflow-131.py'))
    for operation in workflow['OPERATIONS']:
        source = workflow['source131'](operation)
        compile(source, operation, 'exec')
        assert 'StrictHostKeyChecking=yes' in source
        if operation == 'install-commercial-native':
            assert 'estimated131<1800' in source and '32*1024**2' in source
            assert 'deployment-manifest.json' in source
        elif operation == 'run-commercial-native':
            assert 'attempt_count=1' in source and '660' in source
        elif operation == 'retrieve-commercial-evidence':
            assert 'original_udid_guard_passed=True' in source and 'ro,noload' in source
        (REPORT / (operation + '.generated.py')).open('x').write(source)
    result = dict(exact_two_member_module_and_readonly_probe_delta=True,
                  original_composer_runtime_services_seed_and_modules_unchanged=True,
                  full_ordered_overlay_chain_verified=True, backend_glue_seed_and_battery_tests_pass=True,
                  three_isolation_guards_pass=True, cmdline_length_guard_present=True,
                  one_boot_privacy_and_preservation_gates_retained=True)
    (REPORT / 'admission-test.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
