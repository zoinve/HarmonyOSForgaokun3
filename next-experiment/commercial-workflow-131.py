"""Single bounded native battery-module validation, retaining original services."""
from pathlib import Path
import json
import re
import runpy
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REPORT = ROOT / 'reports/commercial61-native-131'
OPERATIONS = ['install-commercial-native', 'run-commercial-native',
              'retrieve-commercial-evidence', 'verify-commercial-return']
configure_local_transport = runpy.run_path(str(BASE / 'commercial-workflow-124.py'))['configure_local_transport']


def source131(operation):
    assert operation in OPERATIONS
    source = (ROOT / 'reports/commercial61-native-130' / (operation + '.generated.py')).read_text()
    source = source.replace('commercial61-native-130', 'commercial61-native-131')
    source = source.replace('commercial-return-audit-130', 'commercial-return-audit-131')
    source = source.replace('ordered_chain_equals_full_130', 'ordered_chain_equals_full_131')
    if operation == 'install-commercial-native':
        overlay = json.loads((REPORT / 'overlay-result.json').read_text())
        source = source.replace("manifest=json.loads((report/'result.json')", "manifest=json.loads((report/'deployment-manifest.json')")
        source, count = re.subn(r"^assert overlay_result\['chain'\]==.*$",
                               "assert overlay_result['chain']==" + repr(overlay['chain']), source, flags=re.M)
        assert count == 1
        source, count = re.subn(r"^assert overlay_result\['shared_parent_overlay_sha256'\]==.*$",
                               "assert overlay_result['shared_parent_overlay_sha256']==" + repr(overlay['shared_parent_overlay_sha256']), source, flags=re.M)
        assert count == 1
        start = source.index("'initrd /commercial61-native-001/initrd.img'")
        end = source.index(',options', start)
        source = source[:start] + ','.join(repr('initrd /' + path) for path in overlay['chain']) + source[end:]
        lines = source.splitlines(keepends=True)
        matches = [i for i, line in enumerate(lines) if line.startswith('estimated130=')]
        assert len(matches) == 1
        index = matches[0]
        lines[index] = lines[index].split(' for p in ', 1)[0].replace('estimated130', 'estimated131') + ' for p in ' + repr(overlay['chain']) + ')+1\n'
        source = ''.join(lines).replace('assert estimated130<1800,estimated130', 'assert estimated131<1800,estimated131')
        source = source.replace('native panel backlight driver 130', 'native EC battery module 131')
        anchor = "images=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/commercial61-original-001')"
        assert source.count(anchor) == 1
        source = source.replace(anchor, "assert sha(esp/'commercial61-native-130/initrd.img')==" + repr(overlay['shared_parent_overlay_sha256']) + '\n' + anchor, 1)
    elif operation == 'retrieve-commercial-evidence':
        previous = json.loads((ROOT / 'reports/commercial61-native-130/runtime-evidence/retrieval-manifest.json').read_text())['run']
        anchor = 'if p.name not in ['
        assert source.count(anchor) == 1
        source = source.replace(anchor, anchor + repr(previous) + ', ', 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in [*OPERATIONS, 'retain-entries']
    assert all(json.loads((REPORT / 'admission-test.json').read_text()).values())
    configure_local_transport()
    if sys.argv[1] == 'retain-entries':
        runpy.run_path(str(BASE / 'retain-latest-experiment-boot-entries-001.py'), run_name='__main__')
    else:
        operation = sys.argv[1]
        source = source131(operation)
        assert source == (REPORT / (operation + '.generated.py')).read_text()
        exec(compile(source, operation, 'exec'), {'__name__': '__main__', '__file__': str(BASE / (operation + '-131.py'))})
