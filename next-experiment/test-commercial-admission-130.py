"""Admit only the exact backlight-only runtime delta and complete overlay chain."""
from pathlib import Path
import gzip
import hashlib
import json
import lzma
import runpy
import shutil
import subprocess
import tempfile

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
BUILD=Path('/home/zoinve/harmony-virgl-883')
def sha(data):return hashlib.sha256(data).hexdigest()

if __name__=='__main__':
    report=ROOT/'reports/commercial61-native-130';work=BUILD/'commercial61-native-130'
    assert not (report/'admission-test.json').exists()
    parse=runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    def members(path):
        data=path.read_bytes()
        raw=lzma.decompress(data) if data.startswith(b'\xfd7zXZ') else gzip.decompress(data)
        return {name:(mode,body) for name,mode,body in parse(raw)}
    before=members(BUILD/'commercial61-native-123/initrd.img');after=members(work/'initrd.img')
    metadata=json.loads((report/'result.json').read_text())
    for row in metadata['artifacts']:assert sha((work/row['name']).read_bytes())==row['sha256']
    driver=metadata['driver130'];library=driver['library_archive_path']
    assert set(before)==set(after)
    assert {name for name in before if before[name]!=after[name]}=={'init','early-hardware093.sh',library}
    for name in ['bootstrap','bootstrap.c','bootstrap-runtime087','bootstrap-runtime087.c']:
        assert (work/name).read_bytes()==(BUILD/'commercial61-native-123'/name).read_bytes()
    assert (work/'init.c').read_text()==runpy.run_path(str(BASE/'build-commercial-native-130.py'))['adapt']((BUILD/'commercial61-native-123/init.c').read_text())
    assert sha(after[library][1])==driver['composer_sha256']
    overlay=json.loads((report/'overlay-result.json').read_text());merged={}
    for relative in overlay['chain']:
        number,filename=relative.split('/')
        if filename=='early094.img':path=BUILD/'commercial61-native-094/minimal-overlay.img'
        elif number=='commercial61-native-001':path=BUILD/relative
        elif number=='commercial61-native-016':path=BUILD/'commercial61-native-016-r2/minimal-overlay.img'
        elif number=='commercial61-native-072':path=BUILD/number/'minimal-overlay-xz.img'
        else:path=BUILD/number/'minimal-overlay.img'
        merged.update(members(path))
    assert merged==after
    for test in ['test-gaokun-basic-sysfs-001.py','test-native-backlight-129.py','test-oobe-seed-123.py']:
        result=subprocess.run(['python3',str(BASE/test),'-v'],capture_output=True)
        (report/(test+'.stdout')).open('xb').write(result.stdout)
        (report/(test+'.stderr')).open('xb').write(result.stderr)
        assert result.returncode==0,result.stderr.decode(errors='replace')
    with tempfile.TemporaryDirectory(prefix='driver130-guard-') as directory:
        for name in ['init','bootstrap','bootstrap-runtime087']:
            binary=Path(directory)/name;shutil.copyfile(work/name,binary);binary.chmod(0o755)
            result=subprocess.run(['qemu-aarch64',str(binary)],capture_output=True,timeout=15)
            assert result.returncode==77,(name,result.returncode,result.stderr)
    permissions=(BASE/'native-backlight-permissions-130.h').read_text()
    assert 'fstatfs(dir, &fs)' in permissions and 'fs.f_type != 0x62656572' in permissions
    assert 'fchown(fd, 0, 3036)' in permissions and 'fchmod(fd, 0660)' in permissions
    workflow=runpy.run_path(str(BASE/'commercial-workflow-130.py'))
    for operation in workflow['OPERATIONS']:
        source=workflow['source130'](operation);compile(source,operation,'exec')
        assert 'StrictHostKeyChecking=yes' in source
        if operation=='install-commercial-native':assert 'estimated130<1800' in source and '32*1024**2' in source
        if operation=='run-commercial-native':assert 'attempt_count=1' in source and '660' in source
        if operation=='retrieve-commercial-evidence':assert 'original_udid_guard_passed=True' in source and 'ro,noload' in source
        (report/(operation+'.generated.py')).open('x').write(source)
    result=dict(exact_three_member_driver_delta=True,original_runtime_services_and_seed_unchanged=True,
        real_sysfs_only_with_narrow_composer_group_rule=True,original_gpu_pipeline_unchanged=True,
        public_composer_exports_preserved=True,full_ordered_overlay_chain_verified=True,
        backend_glue_and_seed_tests_pass=True,three_isolation_guards_pass=True,
        cmdline_length_guard_present=True,one_boot_privacy_and_preservation_gates_retained=True)
    (report/'admission-test.json').open('x').write(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
