"""Admit only the real battery module and bounded read-only outer observation."""
from pathlib import Path
import ast
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
    report = ROOT / 'reports/commercial61-native-133'
    work = BUILD / 'commercial61-native-133'
    parent = BUILD / 'commercial61-native-131'
    assert not (report / 'admission-test.json').exists()
    parse = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    def members(path):
        data = path.read_bytes()
        raw = lzma.decompress(data) if data.startswith(b'\xfd7zXZ') else gzip.decompress(data)
        return {name: (mode, body) for name, mode, body in parse(raw)}
    before, after = members(parent / 'initrd.img'), members(work / 'initrd.img')
    metadata = json.loads((report / 'result.json').read_text())
    parent_metadata = json.loads((ROOT / 'reports/commercial61-native-131/deployment-manifest.json').read_text())
    for folder, manifest in [(work, metadata), (parent, parent_metadata)]:
        for row in manifest['artifacts']:
            assert sha((folder / row['name']).read_bytes()) == row['sha256']
    driver = metadata['driver133']
    module = driver['module_path']
    assert set(before) == set(after)
    assert {name for name in before if before[name] != after[name]} == {'init', 'early-hardware093.sh', module}
    for name in ['bootstrap', 'bootstrap.c', 'bootstrap-runtime087', 'bootstrap-runtime087.c']:
        assert (work / name).read_bytes() == (parent / name).read_bytes()
    source = (work / 'init.c').read_text()
    assert source == runpy.run_path(str(BASE / 'build-commercial-native-133.py'))['adapt']((parent / 'init.c').read_text())
    assert 'probe("oobe-seed-load123",seed123,36)' in source
    assert '02c810f94799cf4b89cc59dea2409981b4678e8b201d60c0ceb62fd7397b21cd' in source
    assert sha(after[module][1]) == driver['module_sha256']
    module_report = json.loads((ROOT / 'reports/commercial-battery-module-132/result.json').read_text())
    module_source = (ROOT / 'reports/commercial-battery-module-132/huawei-gaokun-battery.c').read_text()
    old_source = (BUILD / 'native-binder-kernel-045/linux/drivers/power/supply/huawei-gaokun-battery.c').read_text()
    assert module_source == runpy.run_path(str(BASE / 'build-commercial-battery-module-132.py'))['adapt'](old_source)
    assert sha(module_source.encode()) == module_report['source_sha256']
    overlay = json.loads((report / 'overlay-result.json').read_text())
    assert sha((work / 'minimal-overlay.img').read_bytes()) == overlay['sha256']
    assert set(members(work / 'minimal-overlay.img')) == {'init', 'early-hardware093.sh', module}
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
    assert len(overlay['chain']) == 28
    assert 'commercial61-native-130/initrd.img' in overlay['chain']
    assert 'commercial61-native-131/initrd.img' not in overlay['chain']
    for test in ['test-native-driver-133.py', 'test-commercial-battery-131.py',
                 'test-gaokun-basic-sysfs-001.py', 'test-native-backlight-129.py', 'test-oobe-seed-123.py']:
        result = subprocess.run(['python3', str(BASE / test), '-v'], capture_output=True)
        (report / (test + '.stdout')).open('xb').write(result.stdout)
        (report / (test + '.stderr')).open('xb').write(result.stderr)
        assert result.returncode == 0, result.stderr.decode(errors='replace')
    with tempfile.TemporaryDirectory(prefix='driver133-guard-') as directory:
        for name in ['init', 'bootstrap', 'bootstrap-runtime087']:
            binary = Path(directory) / name
            shutil.copyfile(work / name, binary)
            binary.chmod(0o755)
            result = subprocess.run(['qemu-aarch64', str(binary)], capture_output=True, timeout=15)
            assert result.returncode == 77, (name, result.returncode, result.stderr)
    workflow = runpy.run_path(str(BASE / 'commercial-workflow-133.py'))
    for operation in workflow['OPERATIONS']:
        generated = workflow['source133'](operation)
        tree = ast.parse(generated)
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and '\nfrom pathlib import Path\n' in node.value:
                compile(node.value, operation + '-remote', 'exec')
        assert 'StrictHostKeyChecking=yes' in generated
        if operation == 'install-commercial-native':
            assert 'estimated133<1800' in generated and '32*1024**2' in generated
        elif operation == 'run-commercial-native':
            assert 'attempt_count=1' in generated and '660' in generated
        elif operation == 'retrieve-commercial-evidence':
            assert 'original_udid_guard_passed=True' in generated and 'ro,noload' in generated
        (report / (operation + '.generated.py')).open('x').write(generated)
    result = dict(exact_module_and_readonly_observer_delta=True, real_ec_access_and_charging_code_unchanged=True,
                  original_battery_hdi_and_composer_unchanged=True, original_runtime_and_seed_unchanged=True,
                  seed_copy_budget_bounded_within_existing_outer_deadline=True,
                  full_ordered_overlay_chain_verified=True, focused_tests_pass=True,
                  three_isolation_guards_pass=True, cmdline_length_guard_present=True,
                  one_boot_privacy_and_preservation_gates_retained=True)
    (report / 'admission-test.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
