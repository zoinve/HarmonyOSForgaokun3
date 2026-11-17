"""Check the second entry is exactly the admitted storage runtime, without reset."""
from pathlib import Path
import ast
import gzip
import hashlib
import json
import lzma
import runpy

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
BUILD=Path('/home/zoinve/harmony-virgl-883')
def sha(data):return hashlib.sha256(data).hexdigest()

if __name__=='__main__':
    prior=ROOT/'reports/commercial61-native-166-compile-fix-1'
    report=ROOT/'reports/commercial61-native-167'
    assert not (report/'admission-test.json').exists()
    assert all(json.loads((prior/'admission-test.json').read_text()).values())
    assert json.loads((prior/'persistent-offline-verification.json').read_text())['filesystem_clean']
    parent=BUILD/'commercial61-native-166-compile-fix-1'
    work=BUILD/'commercial61-native-167'
    metadata=json.loads((report/'result.json').read_text())
    for row in metadata['artifacts']:
        assert (work/row['name']).read_bytes()==(parent/row['name']).read_bytes()
        assert sha((work/row['name']).read_bytes())==row['sha256']
    parser=runpy.run_path(str(BASE/'audit-commercial-network-inputs-079.py'))['members']
    def unpack(path):
        data=path.read_bytes()
        raw=lzma.decompress(data) if data.startswith(b'\xfd7zXZ') else gzip.decompress(data)
        return {n:(m,b) for n,m,b in parser(raw)}
    overlay=json.loads((report/'overlay-result.json').read_text())
    merged={}
    for relative in overlay['chain']:
        number,filename=relative.split('/')
        if number=='commercial61-native-001':path=BUILD/relative
        elif number=='commercial61-native-016':path=BUILD/'commercial61-native-016-r2/minimal-overlay.img'
        elif number=='commercial61-native-072':path=BUILD/number/'minimal-overlay-xz.img'
        else:path=BUILD/number/'minimal-overlay.img'
        merged.update(unpack(path))
    assert merged==unpack(work/'initrd.img')
    workflow=runpy.run_path(str(BASE/'commercial-workflow-167.py'))
    for operation in workflow['OPERATIONS']:
        source=workflow['source167'](operation)
        compile(source,operation,'exec')
        for node in ast.walk(ast.parse(source)):
            if isinstance(node,ast.Constant) and isinstance(node.value,str) and '\nfrom pathlib import Path\n' in node.value:
                compile(node.value,operation+'-remote','exec')
        assert 'StrictHostKeyChecking=yes' in source
        if operation=='install-commercial-native':
            assert 'harmony.persistent_data166=1' in source
            assert 'commercial61-native-166/bootstrap-runtime087' in source
            assert 'estimated167<1800' in source and '32*1024**2' in source
        elif operation=='run-commercial-native':assert 'attempt_count=1' in source
        (report/(operation+'.generated.py')).open('x').write(source)
    result=dict(first_boot_offline_check_pass=True,all_artifacts_identical_to_admitted_166=True,
        complete_29_archive_chain_equals_full=True,same_data_file_no_reset=True,
        workflow_oneshot_authentication_and_esp_guards_preserved=True)
    (report/'admission-test.json').open('x').write(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
