"""Single bounded topology-path integration boot, preserving all prior guards."""
from pathlib import Path
import json
import runpy
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REPORT = ROOT / 'reports/commercial61-native-141'
previous = runpy.run_path(str(BASE / 'commercial-workflow-139.py'))
configure_local_transport = previous['configure_local_transport']
OPERATIONS = previous['OPERATIONS']


def source141(operation):
    source = (ROOT / 'reports/commercial61-native-139' / (operation + '.generated.py')).read_text()
    source = source.replace('commercial61-native-139', 'commercial61-native-141')
    source = source.replace('commercial-return-audit-139', 'commercial-return-audit-141')
    source = source.replace('ordered_chain_equals_full_139', 'ordered_chain_equals_full_141')
    source = source.replace('estimated139', 'estimated141')
    if operation == 'install-commercial-native':
        parent = json.loads((ROOT / 'reports/commercial61-native-139/overlay-result.json').read_text())
        overlay = json.loads((REPORT / 'overlay-result.json').read_text())
        old = parent['shared_parent_overlay_sha256']
        new = overlay['shared_parent_overlay_sha256']
        anchor = "assert overlay_result['shared_parent_overlay_sha256']==" + repr(old)
        assert source.count(anchor) == 1
        source = source.replace(anchor, "assert overlay_result['shared_parent_overlay_sha256']==" + repr(new), 1)
        anchor = "assert sha(esp/'commercial61-native-136/initrd.img')==" + repr(old)
        assert source.count(anchor) == 1
        source = source.replace(anchor, "assert sha(esp/'commercial61-native-139/initrd.img')==" + repr(new), 1)
        source = source.replace('native audio binding diagnostics 139', 'native board audio topology integration 141')
        assert repr(overlay['chain']) in source
    elif operation == 'retrieve-commercial-evidence':
        run = json.loads((ROOT / 'reports/commercial61-native-139/runtime-evidence/retrieval-manifest.json').read_text())['run']
        anchor = 'if p.name not in ['
        assert source.count(anchor) == 1
        source = source.replace(anchor, anchor + repr(run) + ', ', 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in [*OPERATIONS, 'retain-entries']
    assert all(json.loads((REPORT / 'admission-test.json').read_text()).values())
    configure_local_transport()
    if sys.argv[1] == 'retain-entries':
        runpy.run_path(str(BASE / 'retain-latest-experiment-boot-entries-001.py'), run_name='__main__')
    else:
        operation = sys.argv[1]
        source = source141(operation)
        assert source == (REPORT / (operation + '.generated.py')).read_text()
        exec(compile(source, operation, 'exec'), {'__name__': '__main__', '__file__': str(BASE / (operation + '-141.py'))})
