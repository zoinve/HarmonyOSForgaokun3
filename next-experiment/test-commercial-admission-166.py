"""Require exact archive reconstruction, real binaries and narrowly scoped changes."""
from pathlib import Path
import ast
import gzip
import hashlib
import json
import lzma
import runpy
import subprocess
import tempfile

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
BUILD=Path('/home/zoinve/harmony-virgl-883')
def sha(data):return hashlib.sha256(data).hexdigest()

if __name__=='__main__':
    report=ROOT/'reports/commercial61-native-166-compile-fix-1'
    assert not (report/'admission-test.json').exists()
    work=BUILD/'commercial61-native-166-compile-fix-1'
    parent=BUILD/'commercial61-native-164'
    parser=runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    def unpack(path):
        data=path.read_bytes()
        raw=lzma.decompress(data) if data.startswith(b'\xfd7zXZ') else gzip.decompress(data)
        return {n:(m,b) for n,m,b in parser(raw)}
    before,after=unpack(parent/'initrd.img'),unpack(work/'initrd.img')
    assert before.keys()==after.keys()
    assert {n for n in before if before[n]!=after[n]}=={'init','early-hardware093.sh'}
    metadata=json.loads((report/'result.json').read_text())
    for row in metadata['artifacts']:assert sha((work/row['name']).read_bytes())==row['sha256']
    generator=runpy.run_path(str(BASE/'build-commercial-native-166.py'))
    assert (work/'bootstrap-runtime087.c').read_text()==generator['runtime166']((parent/'bootstrap-runtime087.c').read_text())
    assert (work/'init.c').read_text()==generator['outer166']((parent/'init.c').read_text(),
        metadata['persistent166']['runtime_bootstrap_sha256'],metadata['persistent166']['filesystem_uuid'])
    for name in ['persistent-data-166.h','persistent-runtime-166.h']:
        key='persistent_header_sha256' if name.startswith('persistent-data') else 'runtime_header_sha256'
        assert sha((BASE/name).read_bytes())==metadata['persistent166'][key]
    for name in ['bootstrap','bootstrap.c','native-usb153','live-debug164','live-debug159']:
        assert (work/name).read_bytes()==(parent/name).read_bytes()
    with tempfile.TemporaryDirectory(prefix='rebuild166-') as directory:
        for name in ['init','bootstrap-runtime087']:
            binary=Path(directory)/name
            args=['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-Werror','-I',str(BASE),'-I',str(work),str(work/(name+'.c'))]
            if name=='init':args.append(str(BASE/'baremetal-diagnostic-core.c'))
            proc=subprocess.run(args+['-o',str(binary)],capture_output=True,timeout=120)
            assert proc.returncode==0,proc.stderr.decode()
            assert binary.read_bytes()==(work/name).read_bytes()
            proc=subprocess.run(['qemu-aarch64',str(binary)],capture_output=True,timeout=15)
            assert proc.returncode==77,(name,proc.returncode,proc.stderr)
    overlay=json.loads((report/'overlay-result.json').read_text())
    assert len(overlay['chain'])==29
    assert set(unpack(work/'minimal-overlay.img'))=={'init','early-hardware093.sh','live-debug159'}
    merged={}
    for relative in overlay['chain']:
        number,filename=relative.split('/')
        if number=='commercial61-native-166':path=work/'minimal-overlay.img'
        elif number=='commercial61-native-001':path=BUILD/relative
        elif number=='commercial61-native-016':path=BUILD/'commercial61-native-016-r2/minimal-overlay.img'
        elif number=='commercial61-native-072':path=BUILD/number/'minimal-overlay-xz.img'
        else:path=BUILD/number/'minimal-overlay.img'
        merged.update(unpack(path))
    assert merged==after
    assert all(not n.endswith('host_ed25519') for n in after)
    tests=['test-persistent-data-166.py','test-live-debug-log-163.py','test-live-debug-loader-164.py',
        'test-live-debug-storage-161.py','test-live-debug-analysis-164.py','test-live-debug-root-158.py',
        'test-live-debug-address-159.py','test-live-debug-discovery-159.py','test-live-debug-reader-156.py',
        'test-native-service-devices-152.py','test-native-input-usb-148.py','test-native-driver-133.py',
        'test-gaokun-basic-sysfs-001.py','test-native-backlight-129.py','test-oobe-seed-123.py']
    for name in tests:
        proc=subprocess.run(['python3',str(BASE/name)],capture_output=True,timeout=120)
        (report/(name+'.stdout')).open('xb').write(proc.stdout)
        (report/(name+'.stderr')).open('xb').write(proc.stderr)
        assert proc.returncode==0,(name,proc.stderr.decode())
        assert b'Ran 0 tests' not in proc.stderr
    workflow=runpy.run_path(str(BASE/'commercial-workflow-166.py'))
    for operation in workflow['OPERATIONS']:
        source=workflow['source166'](operation)
        compile(source,operation,'exec')
        for node in ast.walk(ast.parse(source)):
            if isinstance(node,ast.Constant) and isinstance(node.value,str) and '\nfrom pathlib import Path\n' in node.value:
                compile(node.value,operation+'-remote','exec')
        assert 'StrictHostKeyChecking=yes' in source
        if operation=='install-commercial-native':
            assert 'estimated166<1800' in source and '32*1024**2' in source
            assert 'harmony.persistent_data166=1' in source
            assert 'live-debug-helper-164/live-debug164' in source
        elif operation=='run-commercial-native':assert 'attempt_count=1' in source and '660' in source
        elif operation=='retrieve-commercial-evidence':assert 'ro,noload' in source
        (report/(operation+'.generated.py')).open('x').write(source)
    result=dict(exact_two_member_init_delta=True,original_services_and_drivers_preserved=True,
        complete_29_archive_chain_equals_full=True,reproducible_build_and_guard_tests_pass=True,
        fifteen_focused_test_scripts_pass=True,private_keys_excluded=True,
        authenticated_bounded_workflow_and_esp_guards_preserved=True)
    (report/'admission-test.json').open('x').write(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
