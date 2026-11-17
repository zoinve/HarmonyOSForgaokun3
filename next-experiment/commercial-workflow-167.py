"""Second bounded persistence boot; never retry the completed first boot."""
from pathlib import Path
import json
import runpy
import sys

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
REPORT=ROOT/'reports/commercial61-native-167'
previous=runpy.run_path(str(BASE/'commercial-workflow-166.py'))
configure_local_transport=previous['configure_local_transport']
OPERATIONS=previous['OPERATIONS']

def source167(operation):
    source=previous['source166'](operation)
    source=source.replace('commercial61-native-166-compile-fix-1','commercial61-native-167')
    source=source.replace('commercial61-native-166','commercial61-native-167')
    source=source.replace('commercial-return-audit-166','commercial-return-audit-167')
    source=source.replace('ordered_chain_equals_full_166','ordered_chain_equals_full_167')
    source=source.replace('estimated166','estimated167')
    source=source.replace('native persistent NVMe data 166','native persistent NVMe data second boot 167')
    if operation=='install-commercial-native':
        digest=json.loads((REPORT/'result.json').read_text())['persistent166']['runtime_bootstrap_sha256']
        anchor="status=subprocess.check_output(['bootctl','status','--no-pager'],text=True)"
        assert source.count(anchor)==1
        # The identical init deliberately keeps the already admitted runtime166 path.
        check="assert sha(Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/commercial61-native-166/bootstrap-runtime087'))=="+repr(digest)+'\n'
        source=source.replace(anchor,check+anchor,1)
    elif operation=='retrieve-commercial-evidence':
        newest=json.loads((ROOT/'reports/commercial61-native-166-compile-fix-1/runtime-evidence/retrieval-manifest.json').read_text())['run']
        source=source.replace('if p.name not in [','if p.name not in ['+repr(newest)+', ',1)
    return source

if __name__=='__main__':
    assert len(sys.argv)==2 and sys.argv[1] in [*OPERATIONS,'retain-entries']
    assert all(json.loads((REPORT/'admission-test.json').read_text()).values())
    configure_local_transport()
    if sys.argv[1]=='retain-entries':runpy.run_path(str(BASE/'retain-latest-experiment-boot-entries-001.py'),run_name='__main__')
    else:
        operation=sys.argv[1]
        source=source167(operation)
        assert source==(REPORT/(operation+'.generated.py')).read_text()
        exec(compile(source,operation,'exec'),{'__name__':'__main__','__file__':str(BASE/(operation+'-167.py'))})
