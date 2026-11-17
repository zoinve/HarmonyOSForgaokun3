"""Admit exact topology bytes plus diagnostic bootstrap changes only."""
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
    report = ROOT / 'reports/commercial61-native-141'
    work = BUILD / 'commercial61-native-141'
    parent = BUILD / 'commercial61-native-139'
    assert not (report / 'admission-test.json').exists()
    parser = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    builder = runpy.run_path(str(BASE / 'build-commercial-native-141.py'))
    topology = builder['TOPOLOGY_TARGET']
    def unpack(path):
        raw = path.read_bytes()
        raw = lzma.decompress(raw) if raw.startswith(b'\xfd7zXZ') else gzip.decompress(raw)
        return {n: (m, b) for n, m, b in parser(raw)}
    before, after = unpack(parent / 'initrd.img'), unpack(work / 'initrd.img')
    for folder, number in [(parent, 139), (work, 141)]:
        metadata = json.loads((ROOT / ('reports/commercial61-native-' + str(number)) / 'result.json').read_text())
        for row in metadata['artifacts']:
            assert sha((folder / row['name']).read_bytes()) == row['sha256']
    assert set(after) == set(before) | {topology}
    assert {n for n in after if before.get(n) != after[n]} == {'init', 'early-hardware093.sh', topology}
    assert after[topology] == before[builder['TOPOLOGY_SOURCE']]
    assert sha(after[topology][1]) == builder['TOPOLOGY_SHA']
    assert (work / 'init.c').read_text() == builder['adapt']((parent / 'init.c').read_text())
    header = (BASE / 'native-media-bindings-141.h').read_bytes()
    assert sha(header) == metadata['driver141']['header_sha256']
    for forbidden in [b'O_WRONLY', b'O_RDWR', b'ioctl(', b'probe(', b'modprobe', b'address', b'uevent']:
        assert forbidden not in header
    assert b'now - last >= 20' in header and b'/sys/bus/aprbus/devices' in header
    assert b'MS_NOSUID | MS_NODEV | MS_NOEXEC' in header and b'no_remount=1' in header
    overlay = json.loads((report / 'overlay-result.json').read_text())
    assert sha((work / 'minimal-overlay.img').read_bytes()) == overlay['sha256']
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
        merged.update(unpack(path))
    assert merged == after and len(overlay['chain']) == 28
    for name in ['bootstrap', 'bootstrap.c', 'bootstrap-runtime087', 'bootstrap-runtime087.c']:
        assert (work / name).read_bytes() == (parent / name).read_bytes()
    for test in ['test-native-media-bindings-139.py', 'test-native-media-analysis-138.py', 'test-native-media-136.py',
                 'test-native-driver-133.py', 'test-gaokun-basic-sysfs-001.py', 'test-native-backlight-129.py', 'test-oobe-seed-123.py']:
        result = subprocess.run(['python3', str(BASE / test), '-v'], capture_output=True, timeout=120)
        (report / (test + '.stderr')).open('xb').write(result.stderr)
        (report / (test + '.stdout')).open('xb').write(result.stdout)
        assert result.returncode == 0, result.stderr.decode(errors='replace')
    with tempfile.TemporaryDirectory(prefix='topology141-guard-') as directory:
        for name in ['init', 'bootstrap', 'bootstrap-runtime087']:
            binary = Path(directory) / name
            shutil.copyfile(work / name, binary)
            binary.chmod(0o755)
            result = subprocess.run(['qemu-aarch64', str(binary)], capture_output=True, timeout=15)
            assert result.returncode == 77, (name, result.returncode)
    workflow = runpy.run_path(str(BASE / 'commercial-workflow-141.py'))
    for operation in workflow['OPERATIONS']:
        source = workflow['source141'](operation)
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and '\nfrom pathlib import Path\n' in node.value:
                compile(node.value, operation + '-remote', 'exec')
        assert 'StrictHostKeyChecking=yes' in source
        if operation == 'install-commercial-native':
            assert 'estimated141<1800' in source and '32*1024**2' in source
        elif operation == 'run-commercial-native':
            assert 'attempt_count=1' in source and '660' in source
        elif operation == 'retrieve-commercial-evidence':
            assert 'original_udid_guard_passed=True' in source and 'ro,noload' in source
        (report / (operation + '.generated.py')).open('x').write(source)
    result = dict(exact_three_member_delta=True, full_chain_equals_full_image=True,
                  original_modules_runtime_seed_backends_unchanged=True, exact_board_topology_bytes_preserved=True,
                  bounded_read_only_observation_with_diagnostic_debugfs=True, focused_tests_pass=True,
                  isolation_guards_pass=True, workflow_privacy_boot_and_esp_guards_preserved=True)
    (report / 'admission-test.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
