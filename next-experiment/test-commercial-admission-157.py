"""Verify exact sidecar delta, secret exclusion, workflow and baseline guards."""
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
    report = ROOT / 'reports/commercial61-native-157'
    assert not (report / 'admission-test.json').exists()
    work, parent = BUILD / 'commercial61-native-157', BUILD / 'commercial61-native-153'
    parser = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    def unpack(path):
        raw = path.read_bytes()
        raw = lzma.decompress(raw) if raw.startswith(b'\xfd7zXZ') else gzip.decompress(raw)
        return {n:(m,b) for n,m,b in parser(raw)}
    before, after = unpack(parent / 'initrd.img'),unpack(work / 'initrd.img')
    metadata = json.loads((report / 'result.json').read_text())
    for row in metadata['artifacts']:
        assert sha((work / row['name']).read_bytes()) == row['sha256']
    assert set(after) - set(before) == {'live-debug157','live-debug157-root'}
    assert {n for n in before if before[n] != after[n]} == {'init','early-hardware093.sh'}
    for name in ['bootstrap','bootstrap.c','bootstrap-runtime087','bootstrap-runtime087.c','native-usb153']:
        assert (work / name).read_bytes() == (parent / name).read_bytes()
    package = json.loads((ROOT / 'reports/live-debug-inputs-157/result.json').read_text())
    expected = runpy.run_path(str(BASE / 'build-commercial-native-157.py'))['adapt']((parent / 'init.c').read_text(),package['sha256'])
    assert (work / 'init.c').read_text() == expected
    details = metadata['live157']
    assert sha((BASE / 'native-live-debug-157.h').read_bytes()) == details['header_sha256']
    assert sha((BASE / 'live-debug-launcher-157.c').read_bytes()) == details['helper_source_sha256']
    assert not package['private_key_in_archive'] and not details['private_keys_in_initrd']
    assert all(not n.endswith('host_ed25519') for n in after)
    with tempfile.TemporaryDirectory(prefix='live157-guards-') as directory:
        for name in ['init','bootstrap','bootstrap-runtime087','live-debug157']:
            binary = Path(directory) / name
            shutil.copyfile(work / name,binary)
            binary.chmod(0o755)
            result = subprocess.run(['qemu-aarch64',str(binary),*(['--native-live157','123'] if name == 'live-debug157' else [])],capture_output=True,timeout=15)
            assert result.returncode == 77,(name,result.returncode,result.stderr.decode(errors='replace'))
    programs = subprocess.check_output(['readelf','-lW',str(work / 'live-debug157')],text=True)
    assert 'INTERP' not in programs
    overlay = json.loads((report / 'overlay-result.json').read_text())
    assert sha((work / 'minimal-overlay.img').read_bytes()) == overlay['sha256']
    merged = {}
    for relative in overlay['chain']:
        number, filename = relative.split('/')
        if filename == 'early094.img':path = BUILD / 'commercial61-native-094/minimal-overlay.img'
        elif number == 'commercial61-native-001':path = BUILD / relative
        elif number == 'commercial61-native-016':path = BUILD / 'commercial61-native-016-r2/minimal-overlay.img'
        elif number == 'commercial61-native-072':path = BUILD / number / 'minimal-overlay-xz.img'
        else:path = BUILD / number / 'minimal-overlay.img'
        merged.update(unpack(path))
    assert merged == after and len(overlay['chain']) == 28
    for test in ['test-live-debug-reader-156.py','test-live-debug-launcher-157.py','test-native-service-devices-152.py',
        'test-service-devices-analysis-152.py','test-native-input-usb-148.py','test-input-usb-analysis-148.py',
        'test-native-driver-133.py','test-gaokun-basic-sysfs-001.py','test-native-backlight-129.py','test-oobe-seed-123.py']:
        result = subprocess.run(['python3',str(BASE / test)],capture_output=True,timeout=120)
        (report / (test + '.stdout')).open('xb').write(result.stdout)
        (report / (test + '.stderr')).open('xb').write(result.stderr)
        assert result.returncode == 0,(test,result.stderr.decode(errors='replace'))
    workflow = runpy.run_path(str(BASE / 'commercial-workflow-157.py'))
    for operation in workflow['OPERATIONS']:
        source = workflow['source157'](operation)
        compile(source,operation,'exec')
        for node in ast.walk(ast.parse(source)):
            if isinstance(node,ast.Constant) and isinstance(node.value,str) and '\nfrom pathlib import Path\n' in node.value:
                compile(node.value,operation + '-remote','exec')
        assert 'StrictHostKeyChecking=yes' in source
        if operation == 'install-commercial-native':
            assert 'estimated157<1800' in source and '32*1024**2' in source
            assert 'harmony.live_debug157=1' in source
        elif operation == 'run-commercial-native':assert 'attempt_count=1' in source and '660' in source
        elif operation == 'retrieve-commercial-evidence':assert 'ro,noload' in source and 'original_udid_guard_passed=True' in source
        (report / (operation + '.generated.py')).open('x').write(source)
    result = dict(exact_optional_sidecar_delta=True,original_runtime_seed_services_modules_unchanged=True,
        full_chain_equals_full_image=True,private_keys_excluded_from_initrd_and_archive=True,
        static_helper_and_native_guards_pass=True,focused_and_baseline_tests_pass=True,
        workflow_boot_privacy_esp_guards_preserved=True)
    (report / 'admission-test.json').open('x').write(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
