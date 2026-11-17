"""Admit exact native module bootstrap delta, unchanged device backends/services."""
from pathlib import Path
import ast
import gzip
import hashlib
import json
import lzma
import re
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
    report = ROOT / 'reports/commercial61-native-136'
    work = BUILD / 'commercial61-native-136'
    parent = BUILD / 'commercial61-native-133'
    assert not (report / 'admission-test.json').exists()
    parse = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    def members(path):
        data = path.read_bytes()
        raw = lzma.decompress(data) if data.startswith(b'\xfd7zXZ') else gzip.decompress(data)
        return {name: (mode, body) for name, mode, body in parse(raw)}
    before, after = members(parent / 'initrd.img'), members(work / 'initrd.img')
    metadata = json.loads((report / 'result.json').read_text())
    parent_metadata = json.loads((ROOT / 'reports/commercial61-native-133/result.json').read_text())
    for folder, manifest in [(work, metadata), (parent, parent_metadata)]:
        for row in manifest['artifacts']:
            assert sha((folder / row['name']).read_bytes()) == row['sha256']
    assert set(before) == set(after)
    assert {name for name in before if before[name] != after[name]} == {'init', 'early-hardware093.sh'}
    for name in ['bootstrap', 'bootstrap.c', 'bootstrap-runtime087', 'bootstrap-runtime087.c']:
        assert (work / name).read_bytes() == (parent / name).read_bytes()
    source = (work / 'init.c').read_text()
    assert source == runpy.run_path(str(BASE / 'build-commercial-native-136.py'))['adapt']((parent / 'init.c').read_text())
    assert 'probe("oobe-seed-load123",seed123,36)' in source
    driver = metadata['driver136']
    header_bytes = (BASE / 'native-media-136.h').read_bytes()
    assert sha(header_bytes) == driver['header_sha256']
    header = header_bytes.decode()
    for forbidden in ['O_WRONLY', 'O_RDWR', 'fchmod(', 'fchown(', 'ioctl(', 'tas_bootstrap']:
        assert forbidden not in header
    assert 'native_media136_allowed(start, native_media136_now(), 4)' in header
    assert 'result == 124 || result == 125' in header
    assert 'now - start <= 30 - requested' in header
    block = header.split('native_media136_modules[] = {', 1)[1].split('};', 1)[0]
    modules = re.findall('"([a-z0-9_]+)"', block)
    assert len(modules) == 18 and len(set(modules)) == 18
    audit = json.loads((ROOT / 'reports/audio-bluetooth-payload-135/result.json').read_text())
    checked = {}
    for module in modules:
        candidates = [(name, body) for name, (_, body) in after.items()
                      if name.endswith('.ko') and Path(name).stem.replace('-', '_') == module]
        assert len(candidates) == 1, module
        name, body = candidates[0]
        digest = sha(body)
        if module in audit['native_modules']:
            assert digest == audit['native_modules'][module]['sha256']
        checked[module] = dict(path=name, sha256=digest)
    for processor in audit['remoteproc_firmware'].values():
        assert processor['packaged']
        for row in processor['files']:
            assert sha(after[row['path']][1]) == row['sha256']
    overlay = json.loads((report / 'overlay-result.json').read_text())
    assert sha((work / 'minimal-overlay.img').read_bytes()) == overlay['sha256']
    minimal = members(work / 'minimal-overlay.img')
    assert set(minimal) == set(overlay['members'])
    assert all(value == after[name] for name, value in minimal.items())
    assert set(minimal) == {'init', 'early-hardware093.sh', metadata['driver133']['module_path']}
    assert sha(after[metadata['driver133']['module_path']][1]) == metadata['driver133']['module_sha256']
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
    for test in ['test-native-media-136.py', 'test-native-driver-133.py',
                 'test-gaokun-basic-sysfs-001.py', 'test-native-backlight-129.py', 'test-oobe-seed-123.py']:
        result = subprocess.run(['python3', str(BASE / test), '-v'], capture_output=True)
        (report / (test + '.stdout')).open('xb').write(result.stdout)
        (report / (test + '.stderr')).open('xb').write(result.stderr)
        assert result.returncode == 0, result.stderr.decode(errors='replace')
    with tempfile.TemporaryDirectory(prefix='driver136-guard-') as directory:
        for name in ['init', 'bootstrap', 'bootstrap-runtime087']:
            binary = Path(directory) / name
            shutil.copyfile(work / name, binary)
            binary.chmod(0o755)
            result = subprocess.run(['qemu-aarch64', str(binary)], capture_output=True, timeout=15)
            assert result.returncode == 77, (name, result.returncode, result.stderr)
    workflow = runpy.run_path(str(BASE / 'commercial-workflow-136.py'))
    for operation in workflow['OPERATIONS']:
        generated = workflow['source136'](operation)
        tree = ast.parse(generated)
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and '\nfrom pathlib import Path\n' in node.value:
                compile(node.value, operation + '-remote', 'exec')
        assert 'StrictHostKeyChecking=yes' in generated
        if operation == 'install-commercial-native':
            assert 'estimated136<1800' in generated and '32*1024**2' in generated
        elif operation == 'run-commercial-native':
            assert 'attempt_count=1' in generated and '660' in generated
        elif operation == 'retrieve-commercial-evidence':
            assert 'original_udid_guard_passed=True' in generated and 'ro,noload' in generated
        (report / (operation + '.generated.py')).open('x').write(generated)
    (report / 'verified-media-modules.json').open('x').write(json.dumps(checked, indent=2))
    result = dict(exact_two_member_module_bootstrap_delta=True, original_services_and_hardware_backend_bytes_unchanged=True,
                  original_battery_composer_runtime_seed_and_firmware_unchanged=True,
                  group_and_per_module_admission_limits_present=True, observation_has_no_device_control_writes=True,
                  selected_packaged_modules_and_firmware_hash_verified=True,
                  full_ordered_overlay_chain_verified=True, focused_tests_pass=True,
                  three_isolation_guards_pass=True, cmdline_length_guard_present=True,
                  one_boot_privacy_and_preservation_gates_retained=True)
    (report / 'admission-test.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
