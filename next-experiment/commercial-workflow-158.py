"""Single bounded diagnostic with target-root-aware verification."""
from pathlib import Path
import json
import runpy
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REPORT = ROOT / 'reports/commercial61-native-158'
previous = runpy.run_path(str(BASE / 'commercial-workflow-157.py'))
configure_local_transport = previous['configure_local_transport']
OPERATIONS = previous['OPERATIONS']


def source158(operation):
    source = (ROOT / 'reports/commercial61-native-157' / (operation + '.generated.py')).read_text()
    source = source.replace('commercial61-native-157','commercial61-native-158')
    source = source.replace('commercial-return-audit-157','commercial-return-audit-158')
    source = source.replace('ordered_chain_equals_full_157','ordered_chain_equals_full_158')
    source = source.replace('estimated157','estimated158')
    if operation == 'install-commercial-native':
        parent = json.loads((ROOT / 'reports/commercial61-native-157/overlay-result.json').read_text())
        overlay = json.loads((REPORT / 'overlay-result.json').read_text())
        old, new = parent['shared_parent_overlay_sha256'], overlay['shared_parent_overlay_sha256']
        anchor = "assert overlay_result['shared_parent_overlay_sha256']==" + repr(old)
        assert source.count(anchor) == 1
        source = source.replace(anchor,"assert overlay_result['shared_parent_overlay_sha256']==" + repr(new),1)
        anchor = "assert sha(esp/'commercial61-native-153/initrd.img')==" + repr(old)
        assert source.count(anchor) == 1
        source = source.replace(anchor,"assert sha(esp/'commercial61-native-157/initrd.img')==" + repr(new),1)
        source = source.replace('native authenticated live diagnostic 157','native target-root-aware live diagnostic 158')
        source = source.replace('harmony.live_debug157=1','harmony.live_debug158=1')
        assert repr(overlay['chain']) in source
    elif operation == 'retrieve-commercial-evidence':
        run = json.loads((ROOT / 'reports/commercial61-native-157/runtime-evidence/retrieval-manifest.json').read_text())['run']
        anchor = 'if p.name not in ['
        assert source.count(anchor) == 1
        source = source.replace(anchor,anchor + repr(run) + ', ',1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in [*OPERATIONS,'retain-entries']
    assert all(json.loads((REPORT / 'admission-test.json').read_text()).values())
    configure_local_transport()
    if sys.argv[1] == 'retain-entries':
        runpy.run_path(str(BASE / 'retain-latest-experiment-boot-entries-001.py'),run_name='__main__')
    else:
        operation = sys.argv[1]
        source = source158(operation)
        assert source == (REPORT / (operation + '.generated.py')).read_text()
        exec(compile(source,operation,'exec'),{'__name__':'__main__','__file__':str(BASE / (operation + '-158.py'))})
