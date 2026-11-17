'''Verify the isolated candidate, actual archive chain and bounded non-USB workflow.'''
from pathlib import Path
import ast
import gzip
import hashlib
import json
import lzma
import runpy
import subprocess
import tempfile
import uuid

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
BUILD=Path('/home/zoinve/harmony-virgl-883')
REPORT=ROOT/'reports/commercial61-native-197-r1'


def sha(data):return hashlib.sha256(data).hexdigest()


def main():
    assert not (REPORT/'admission-test.json').exists()
    logs=REPORT/'admission-001';assert not logs.exists();logs.mkdir()
    work=BUILD/'commercial61-native-197-r1';parent=BUILD/'commercial61-native-173'
    parser=runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    def unpack(path):
        data=path.read_bytes()
        raw=lzma.decompress(data) if data.startswith(b'\xfd7zXZ') else gzip.decompress(data)
        return {n:(m,b) for n,m,b in parser(raw)}
    metadata=json.loads((REPORT/'result.json').read_text())
    for row in metadata['artifacts']:assert sha((work/row['name']).read_bytes())==row['sha256']
    before,after=unpack(parent/'initrd.img'),unpack(work/'initrd.img')
    assert before.keys()==after.keys()
    assert {n for n in before if before[n]!=after[n]}=={'init','early-hardware093.sh'}
    for name in ['bootstrap-runtime087','bootstrap-runtime087.c','bootstrap','bootstrap.c','native-usb153','live-debug164','live-debug159']:
        assert (work/name).read_bytes()==(parent/name).read_bytes()
    assert sha((work/'bootstrap-runtime087').read_bytes())=='fe80eef0831fda293ff0bbebb66f9c2d0c6c8c6b739b47cc8714653479ea7122'
    expected=(parent/'init.c').read_text().replace('/commercial61-native-173/bootstrap-runtime087','/commercial61-native-197/bootstrap-runtime087')
    lines=expected.splitlines(keepends=True)
    matches=[i for i,line in enumerate(lines) if line.startswith('#define PERSISTENT166_UUID ')]
    assert len(matches)==1
    lines[matches[0]]='#define PERSISTENT166_UUID {'+','.join(str(v) for v in uuid.UUID('b8383c4f-844b-46cc-9d67-34a3745b3f1f').bytes)+'}\n'
    assert (work/'init.c').read_text()==''.join(lines)
    assert (work/'persistent-data-166.h').read_bytes()==(BASE/'persistent-data-166.h').read_bytes().replace(b'harmony-persistent-data-165',b'harmony-settings-data-197')
    assert (work/'persistent-data-172.h').read_bytes()==(BASE/'persistent-data-172.h').read_bytes()
    with tempfile.TemporaryDirectory(prefix='rebuild197-') as directory:
        for name in ['init','bootstrap-runtime087']:
            binary=Path(directory)/name
            args=['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-Werror','-I',str(BASE),str(work/(name+'.c'))]
            if name=='init':args.append(str(BASE/'baremetal-diagnostic-core.c'))
            proc=subprocess.run(args+['-o',str(binary)],capture_output=True,timeout=120)
            assert proc.returncode==0,proc.stderr.decode()
            assert binary.read_bytes()==(work/name).read_bytes()
            proc=subprocess.run(['qemu-aarch64',str(binary)],capture_output=True,timeout=15)
            assert proc.returncode==77,(name,proc.returncode,proc.stderr)
    overlay=json.loads((REPORT/'overlay-result.json').read_text())
    assert len(overlay['chain'])==29
    assert set(unpack(work/'minimal-overlay.img'))=={'init','early-hardware093.sh','live-debug159'}
    merged={}
    for relative in overlay['chain']:
        number,filename=relative.split('/')
        if number=='commercial61-native-197':path=work/'minimal-overlay.img'
        elif number=='commercial61-native-001':path=BUILD/relative
        elif number=='commercial61-native-016':path=BUILD/'commercial61-native-016-r2/minimal-overlay.img'
        elif number=='commercial61-native-072':path=BUILD/number/'minimal-overlay-xz.img'
        else:path=BUILD/number/'minimal-overlay.img'
        merged.update(unpack(path))
    assert merged==after
    assert all(not n.endswith('host_ed25519') for n in after)
    tests=['test-persistent-runtime-173.py','test-persistent-lifecycle-172.py','test-persistent-runtime-168.py',
        'test-persistent-data-166.py','test-live-debug-log-163.py','test-live-debug-loader-164.py',
        'test-live-debug-storage-161.py','test-live-debug-analysis-164.py','test-live-debug-root-158.py',
        'test-live-debug-address-159.py','test-live-debug-discovery-159.py','test-live-debug-reader-156.py',
        'test-native-service-devices-152.py','test-native-input-usb-148.py','test-native-driver-133.py',
        'test-gaokun-basic-sysfs-001.py','test-native-backlight-129.py','test-oobe-seed-123.py']
    for name in tests:
        proc=subprocess.run(['python3',str(BASE/name)],capture_output=True,timeout=120)
        for suffix,data in [('stdout',proc.stdout),('stderr',proc.stderr)]:
            (logs/(name+'.'+suffix)).open('xb').write(data)
        assert proc.returncode==0 and b'Ran 0 tests' not in proc.stderr,(name,proc.stderr.decode())
    workflow=runpy.run_path(str(BASE/'commercial-workflow-197.py'))
    compile(workflow['PREFLIGHT'],'preflight197','exec')
    deploy=runpy.run_path(str(BASE/'deploy-settings-data-198-r1.py'))['payload']()
    compile(deploy,'deploy198-r1','exec')
    assert 'total<=8589934592' in deploy and 'os.posix_fallocate' in deploy
    for operation in workflow['OPERATIONS']:
        source=workflow['source197'](operation)
        compile(source,operation,'exec')
        tree=ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node,ast.Constant) and isinstance(node.value,str) and '\nfrom pathlib import Path\n' in node.value:
                compile(node.value,operation+'-remote','exec')
        assert 'StrictHostKeyChecking=yes' in source
        assert 'usb176_preflight' not in source and 'usb175' not in source
        if operation=='install-commercial-native':
            assert source.index('assert estimated197<1800')<source.index('root.mkdir()')
            assert source.index('settings197_preflight()\n')<source.index('root.mkdir()')
            assert '32*1024**2' in source and 'harmony.persistent_data166=1' in source
            assert "'initrd /set197.img'" in source
        elif operation=='run-commercial-native':
            assert 'attempt_count=1' in source and '660' in source and 'set197.img' in source
        elif operation=='retrieve-commercial-evidence':
            assert 'ro,noload' in source
            for folder,name in [('commercial61-native-173','runtime-evidence/retrieval-manifest.json'),
                                ('commercial61-native-175-compile-fix-1','early-return-inspection.json')]:
                assert json.loads((ROOT/'reports'/folder/name).read_text())['run'] in source
        (REPORT/(operation+'.generated.py')).open('x').write(source)
    result=dict(exact_two_member_init_delta=True,desktop173_runtime_and_source_byte_identical=True,
        isolated_path_uuid_and_unchanged_persistent_guards=True,complete_29_archive_chain_independently_equals_full=True,
        reproducible_binaries_and_non_pid1_guards=True,eighteen_focused_test_scripts_pass=True,
        workflow_and_remote_sources_compile=True,early_commandline_and_candidate_admission=True,
        prior173_and175_runs_excluded=True,original_security_and_usb_checkpoint_preserved=True)
    (REPORT/'admission-test.json').open('x').write(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
