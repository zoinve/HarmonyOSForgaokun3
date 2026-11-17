"""One bounded persistent-data boot, with all existing preservation guards."""
from pathlib import Path
import json
import runpy
import sys

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
REPORT=ROOT/'reports/commercial61-native-166-compile-fix-1'
previous=runpy.run_path(str(BASE/'commercial-workflow-164.py'))
configure_local_transport=previous['configure_local_transport']
OPERATIONS=previous['OPERATIONS']

def source166(operation):
    source=(ROOT/'reports/commercial61-native-164'/(operation+'.generated.py')).read_text()
    source=source.replace('commercial61-native-164','commercial61-native-166')
    source=source.replace('commercial-return-audit-164','commercial-return-audit-166')
    source=source.replace('ordered_chain_equals_full_164','ordered_chain_equals_full_166')
    source=source.replace('estimated164','estimated166')
    source=source.replace('native current-namespace log diagnostic 164','native persistent NVMe data 166')
    source=source.replace("/'reports/commercial61-native-166'","/'reports/commercial61-native-166-compile-fix-1'")
    source=source.replace('/home/zoinve/harmony-virgl-883/commercial61-native-166/',
        '/home/zoinve/harmony-virgl-883/commercial61-native-166-compile-fix-1/')
    if operation=='install-commercial-native':
        digest=json.loads((REPORT/'result.json').read_text())['persistent166']['runtime_bootstrap_sha256']
        old="assert sha(root/'bootstrap-runtime087')=='81c2fb7d8a613b683c9ed6e4d278032f6dd7626af7995f263839bca791f9dda2'"
        assert source.count(old)==1
        source=source.replace(old,"assert sha(root/'bootstrap-runtime087')=="+repr(digest),1)
        old=' harmony.commercial=1 harmony.live_debug159=1'
        assert source.count(old)==1
        source=source.replace(old,old+' harmony.persistent_data166=1',1)
    elif operation=='retrieve-commercial-evidence':
        latest=json.loads((ROOT/'reports/commercial61-native-164/runtime-evidence/retrieval-manifest.json').read_text())['run']
        assert source.count('if p.name not in [')==1
        source=source.replace('if p.name not in [','if p.name not in ['+repr(latest)+', ',1)
    return source

if __name__=='__main__':
    assert len(sys.argv)==2 and sys.argv[1] in [*OPERATIONS,'retain-entries']
    assert all(json.loads((REPORT/'admission-test.json').read_text()).values())
    configure_local_transport()
    if sys.argv[1]=='retain-entries':
        runpy.run_path(str(BASE/'retain-latest-experiment-boot-entries-001.py'),run_name='__main__')
    else:
        operation=sys.argv[1]
        source=source166(operation)
        assert source==(REPORT/(operation+'.generated.py')).read_text()
        exec(compile(source,operation,'exec'),{'__name__':'__main__','__file__':str(BASE/(operation+'-166.py'))})
