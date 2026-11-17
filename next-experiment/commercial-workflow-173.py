"""One bounded diagnostic with preserved application data and per-boot log history."""
from pathlib import Path
import json
import runpy
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REPORT = ROOT / 'reports/commercial61-native-173'
PREVIOUS = runpy.run_path(str(BASE / 'commercial-workflow-168.py'))
configure_local_transport = PREVIOUS['configure_local_transport']
OPERATIONS = PREVIOUS['OPERATIONS']

def source173(operation):
    source = PREVIOUS['source168'](operation)
    source = source.replace('commercial61-native-168','commercial61-native-173')
    source = source.replace('commercial-return-audit-168','commercial-return-audit-173')
    source = source.replace('ordered_chain_equals_full_168','ordered_chain_equals_full_173')
    source = source.replace('estimated168','estimated173')
    source = source.replace('native persistent NVMe data history fix 168',
        'native persistent NVMe data diagnostics history and teardown 173')
    if operation == 'install-commercial-native':
        old = json.loads((ROOT / 'reports/commercial61-native-168/result.json').read_text())['persistent166']['runtime_bootstrap_sha256']
        new = json.loads((REPORT / 'result.json').read_text())['persistent166']['runtime_bootstrap_sha256']
        assert source.count(old) == 1
        source = source.replace(old,new,1)
    elif operation == 'retrieve-commercial-evidence':
        run = json.loads((ROOT / 'reports/commercial61-native-168/runtime-evidence/retrieval-manifest.json').read_text())['run']
        assert source.count('if p.name not in [') == 1
        source = source.replace('if p.name not in [','if p.name not in [' + repr(run) + ', ',1)
    return source

if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in [*OPERATIONS,'retain-entries']
    assert all(json.loads((REPORT / 'admission-test.json').read_text()).values())
    configure_local_transport()
    if sys.argv[1] == 'retain-entries':
        runpy.run_path(str(BASE / 'retain-latest-experiment-boot-entries-001.py'),run_name='__main__')
    else:
        operation = sys.argv[1]
        source = source173(operation)
        assert source == (REPORT / (operation + '.generated.py')).read_text()
        exec(compile(source,operation,'exec'),
            {'__name__':'__main__','__file__':str(BASE / (operation + '-173.py'))})
