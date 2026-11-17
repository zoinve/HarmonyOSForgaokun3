"""One guarded native service-root diagnostic; never rerun completed 148."""
from pathlib import Path
import json
import runpy
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REPORT = ROOT / 'reports/commercial61-native-152'
previous = runpy.run_path(str(BASE / 'commercial-workflow-148.py'))
configure_local_transport = previous['configure_local_transport']
OPERATIONS = previous['OPERATIONS']


def source152(operation):
    source = (ROOT / 'reports/commercial61-native-148' / (operation + '.generated.py')).read_text()
    source = source.replace('commercial61-native-148', 'commercial61-native-152')
    source = source.replace('commercial-return-audit-148', 'commercial-return-audit-152')
    source = source.replace('ordered_chain_equals_full_148', 'ordered_chain_equals_full_152')
    source = source.replace('estimated148', 'estimated152')
    if operation == 'install-commercial-native':
        parent = json.loads((ROOT / 'reports/commercial61-native-148/overlay-result.json').read_text())
        overlay = json.loads((REPORT / 'overlay-result.json').read_text())
        old, new = parent['shared_parent_overlay_sha256'], overlay['shared_parent_overlay_sha256']
        anchor = "assert overlay_result['shared_parent_overlay_sha256']==" + repr(old)
        assert source.count(anchor) == 1
        source = source.replace(anchor, "assert overlay_result['shared_parent_overlay_sha256']==" + repr(new), 1)
        anchor = "assert sha(esp/'commercial61-native-145/initrd.img')==" + repr(old)
        assert source.count(anchor) == 1
        source = source.replace(anchor, "assert sha(esp/'commercial61-native-148/initrd.img')==" + repr(new), 1)
        source = source.replace('native input and USB integration 148', 'native service device integration 152')
        assert repr(overlay['chain']) in source
    elif operation == 'retrieve-commercial-evidence':
        run = json.loads((ROOT / 'reports/commercial61-native-148/runtime-evidence/retrieval-manifest.json').read_text())['run']
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
        source = source152(operation)
        assert source == (REPORT / (operation + '.generated.py')).read_text()
        exec(compile(source, operation, 'exec'), {'__name__': '__main__', '__file__': str(BASE / (operation + '-152.py'))})
