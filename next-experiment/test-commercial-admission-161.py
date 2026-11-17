"""Verify tiny overlay, exact parent preservation, helper provenance and bounded workflow."""
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
    report = ROOT / 'reports/commercial61-native-161'
    assert not (report / 'admission-test.json').exists()
    work,parent = BUILD / 'commercial61-native-161',BUILD / 'commercial61-native-159'
    parser = runpy.run_path(str(BASE / 'audit-commercial-network-inputs-079.py'))['members']
    def unpack(path):
        data=path.read_bytes()
        raw=lzma.decompress(data) if data.startswith(b'\xfd7zXZ') else gzip.decompress(data)
        return {n:(m,b) for n,m,b in parser(raw)}
    before,after = unpack(parent / 'initrd.img'),unpack(work / 'initrd.img')
    assert before.keys()==after.keys()
    assert {name for name in before if before[name]!=after[name]}=={'live-debug159'}
    metadata=json.loads((report / 'result.json').read_text())
    for row in metadata['artifacts']:
        assert sha((work / row['name']).read_bytes())==row['sha256']
    for name in ['init','init.c','bootstrap','bootstrap.c','bootstrap-runtime087','bootstrap-runtime087.c','native-usb153']:
        assert (work / name).read_bytes()==(parent / name).read_bytes()
    generator=runpy.run_path(str(BASE / 'build-commercial-native-161.py'))
    assert (work / 'live-debug-launcher-161.c').read_text()==generator['helper_source161']()
    assert after['live-debug159'][1].decode()==generator['loader161'](metadata['live161']['helper_sha256'])
    assert sha((BASE / 'live-debug-storage-161.h').read_bytes())==metadata['live161']['storage_header_sha256']
    with tempfile.TemporaryDirectory(prefix='rebuild161-') as directory:
        binary=Path(directory)/'helper'
        compiled=subprocess.run(['aarch64-linux-gnu-gcc','-static','-Os','-s','-Wall','-Wextra','-Werror','-I',str(BASE),
            str(work / 'live-debug-launcher-161.c'),'-o',str(binary)],capture_output=True,timeout=60)
        assert compiled.returncode==0,compiled.stderr.decode()
        assert binary.read_bytes()==(work / 'live-debug161').read_bytes()
        for name in ['init','bootstrap','bootstrap-runtime087','live-debug161']:
            candidate=Path(directory)/name
            shutil.copyfile(work/name,candidate);candidate.chmod(0o755)
            result=subprocess.run(['qemu-aarch64',str(candidate),*(['--native-live159','123'] if name=='live-debug161' else [])],capture_output=True,timeout=15)
            assert result.returncode==77,(name,result.returncode,result.stderr)
    assert 'INTERP' not in subprocess.check_output(['readelf','-lW',str(work / 'live-debug161')],text=True)
    overlay=json.loads((report / 'overlay-result.json').read_text())
    assert len(overlay['chain'])==29 and overlay['bytes']<4096
    assert unpack(work / 'minimal-overlay.img')=={'live-debug159':after['live-debug159']}
    merged={}
    for relative in overlay['chain']:
        number,filename=relative.split('/')
        if filename=='early094.img': path=BUILD/'commercial61-native-094/minimal-overlay.img'
        elif number=='commercial61-native-001': path=BUILD/relative
        elif number=='commercial61-native-016': path=BUILD/'commercial61-native-016-r2/minimal-overlay.img'
        elif number=='commercial61-native-072': path=BUILD/number/'minimal-overlay-xz.img'
        else: path=BUILD/number/'minimal-overlay.img'
        merged.update(unpack(path))
    assert merged==after
    assert all(not name.endswith('host_ed25519') for name in after)
    tests=['test-live-debug-loader-161.py','test-live-debug-storage-161.py','test-live-debug-analysis-159.py',
        'test-live-debug-root-158.py','test-live-debug-address-159.py','test-live-debug-discovery-159.py',
        'test-live-debug-reader-156.py','test-live-debug-launcher-157.py','test-native-service-devices-152.py',
        'test-service-devices-analysis-152.py','test-native-input-usb-148.py','test-input-usb-analysis-148.py',
        'test-native-driver-133.py','test-gaokun-basic-sysfs-001.py','test-native-backlight-129.py','test-oobe-seed-123.py']
    for test in tests:
        result=subprocess.run(['python3',str(BASE/test)],capture_output=True,timeout=120)
        (report/(test+'.stdout')).open('xb').write(result.stdout)
        (report/(test+'.stderr')).open('xb').write(result.stderr)
        assert result.returncode==0,(test,result.stderr.decode(errors='replace'))
    workflow=runpy.run_path(str(BASE/'commercial-workflow-161.py'))
    for operation in workflow['OPERATIONS']:
        source=workflow['source161'](operation)
        compile(source,operation,'exec')
        for node in ast.walk(ast.parse(source)):
            if isinstance(node,ast.Constant) and isinstance(node.value,str) and '\nfrom pathlib import Path\n' in node.value:
                compile(node.value,operation+'-remote','exec')
        assert 'StrictHostKeyChecking=yes' in source
        if operation=='install-commercial-native':
            assert 'estimated161<1800' in source and '32*1024**2' in source
            assert 'harmony.live_debug159=1' in source and 'live-debug-helper-161/live-debug161' in source
        elif operation=='run-commercial-native':assert 'attempt_count=1' in source and '660' in source
        elif operation=='retrieve-commercial-evidence':assert 'ro,noload' in source and 'original_udid_guard_passed=True' in source
        (report/(operation+'.generated.py')).open('x').write(source)
    result=dict(exact_single_loader_delta=True,original_init_services_seed_drivers_unchanged=True,
        complete_29_archive_chain_equals_full=True,helper_rebuild_and_guards_pass=True,
        private_keys_excluded_from_overlay=True,all_16_focused_baseline_scripts_pass=True,
        workflow_authentication_boot_privacy_esp_guards_preserved=True)
    (report/'admission-test.json').open('x').write(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
