"""Prove the exact helper/script delta and original runtime/boot preservation."""
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
    report = ROOT / 'reports/commercial61-native-153'
    work, parent = BUILD / 'commercial61-native-153', BUILD / 'commercial61-native-152'
    assert not (report / 'admission-test.json').exists()
    parser = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    def unpack(path):
        raw = path.read_bytes()
        raw = lzma.decompress(raw) if raw.startswith(b'\xfd7zXZ') else gzip.decompress(raw)
        return {n: (m, b) for n, m, b in parser(raw)}
    before, after = unpack(parent / 'initrd.img'), unpack(work / 'initrd.img')
    for folder, number in [(parent, 152), (work, 153)]:
        metadata = json.loads((ROOT / ('reports/commercial61-native-' + str(number)) / 'result.json').read_text())
        for row in metadata['artifacts']:
            assert sha((folder / row['name']).read_bytes()) == row['sha256']
    key, helper = 'native-target/commercial-desktop077.sh', 'native-target/native-usb153'
    assert set(before) <= set(after) and set(after) - set(before) == {helper}
    assert {n for n in before if before[n] != after[n]} == {key}
    adapt = runpy.run_path(str(BASE / 'build-commercial-native-153.py'))['adapt_script']
    details = metadata['usb153']
    assert sha((BASE / 'native-usb-enumerate-153.c').read_bytes()) == details['source_sha256']
    assert after[key][1] == adapt(before[key][1].decode(), details['helper_sha256'], details['original_library_sha256']).encode()
    assert sha(after[helper][1]) == details['helper_sha256']
    assert sha((ROOT / 'reports/usb-implementation-151/2-libusb_shared.z.so').read_bytes()) == details['original_library_sha256']
    for name in ['init', 'init.c', 'bootstrap', 'bootstrap.c', 'bootstrap-runtime087', 'bootstrap-runtime087.c']:
        assert (work / name).read_bytes() == (parent / name).read_bytes()
    subprocess.run(['/bin/sh', '-n'], input=after[key][1], check=True, timeout=5)
    assert b'/system/bin/timeout 8 /native-usb153' in after[key][1]
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
    for test in ['test-native-usb-enumerate-153.py', 'test-native-service-devices-152.py',
                 'test-service-devices-analysis-152.py', 'test-native-input-usb-148.py', 'test-input-usb-analysis-148.py',
                 'test-native-driver-133.py', 'test-gaokun-basic-sysfs-001.py', 'test-native-backlight-129.py', 'test-oobe-seed-123.py']:
        result = subprocess.run(['python3', str(BASE / test), '-v'], capture_output=True, timeout=120)
        (report / (test + '.stderr')).open('xb').write(result.stderr)
        (report / (test + '.stdout')).open('xb').write(result.stdout)
        assert result.returncode == 0, result.stderr.decode(errors='replace')
    with tempfile.TemporaryDirectory(prefix='usb153-guard-') as directory:
        root = Path(directory)
        for name in ['init', 'bootstrap', 'bootstrap-runtime087']:
            binary = root / name
            shutil.copyfile(work / name, binary)
            binary.chmod(0o755)
            result = subprocess.run(['qemu-aarch64', str(binary)], capture_output=True, timeout=15)
            assert result.returncode == 77, (name, result.returncode)
        headers = subprocess.check_output(['readelf', '-lW', str(work / 'native-usb153')], text=True)
        interpreter = re.search(r'\[Requesting program interpreter: (/[^\]]+)\]', headers)[1]
        assert interpreter.startswith('/lib/') and '..' not in interpreter
        loader = root / interpreter.lstrip('/')
        loader.parent.mkdir(parents=True)
        libc = BUILD / 'commercial-graphics-014/runtime/libc.so'
        shutil.copyfile(libc, loader)
        shutil.copyfile(libc, root / 'lib/libc.so')
        result = subprocess.run(['qemu-aarch64', '-L', str(root), '-E', 'LD_LIBRARY_PATH=/lib',
            str(work / 'native-usb153'), '--enumerate-original-backend'], capture_output=True, timeout=15)
        (report / 'native-helper-guard.stderr').open('xb').write(result.stderr)
        assert result.returncode == 77, (result.returncode, result.stderr.decode(errors='replace'))
    workflow = runpy.run_path(str(BASE / 'commercial-workflow-153.py'))
    for operation in workflow['OPERATIONS']:
        source = workflow['source153'](operation)
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and '\nfrom pathlib import Path\n' in node.value:
                compile(node.value, operation + '-remote', 'exec')
        assert 'StrictHostKeyChecking=yes' in source
        if operation == 'install-commercial-native':
            assert 'estimated153<1800' in source and '32*1024**2' in source
        elif operation == 'run-commercial-native':
            assert 'attempt_count=1' in source and '660' in source
        elif operation == 'retrieve-commercial-evidence':
            assert 'original_udid_guard_passed=True' in source and 'ro,noload' in source
        (report / (operation + '.generated.py')).open('x').write(source)
    result = dict(exact_one_script_change_and_one_helper_addition=True, full_chain_equals_full_image=True,
        original_init_runtime_services_modules_dtb_unchanged=True, original_library_and_helper_hashes_verified=True,
        bounded_readonly_enumeration=True, focused_tests_pass=True, isolation_guards_pass=True,
        workflow_privacy_boot_and_esp_guards_preserved=True)
    (report / 'admission-test.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
