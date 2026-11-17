"""Preserved bounded single-boot workflow for read-only binding diagnostics."""
from pathlib import Path
import json
import re
import runpy
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REPORT = ROOT / 'reports/commercial61-native-139'
previous = runpy.run_path(str(BASE / 'commercial-workflow-136.py'))
configure_local_transport = previous['configure_local_transport']
OPERATIONS = previous['OPERATIONS']


def source139(operation):
    source = (ROOT / 'reports/commercial61-native-136' / (operation + '.generated.py')).read_text()
    source = source.replace('commercial61-native-136', 'commercial61-native-139')
    source = source.replace('commercial-return-audit-136', 'commercial-return-audit-139')
    source = source.replace('ordered_chain_equals_full_136', 'ordered_chain_equals_full_139')
    if operation == 'install-commercial-native':
        overlay = json.loads((REPORT / 'overlay-result.json').read_text())
        for key, value in [('chain', overlay['chain']), ('shared_parent_overlay_sha256', overlay['shared_parent_overlay_sha256'])]:
            source, count = re.subn(r"^assert overlay_result\['" + key + r"'\]==.*$",
                                   "assert overlay_result['" + key + "']==" + repr(value), source, flags=re.M)
            assert count == 1
        start = source.index("'initrd /commercial61-native-001/initrd.img'")
        end = source.index(',options', start)
        source = source[:start] + ','.join(repr('initrd /' + p) for p in overlay['chain']) + source[end:]
        lines = source.splitlines(keepends=True)
        matches = [i for i, line in enumerate(lines) if line.startswith('estimated136=')]
        assert len(matches) == 1
        index = matches[0]
        lines[index] = lines[index].split(' for p in ', 1)[0].replace('estimated136', 'estimated139') + ' for p in ' + repr(overlay['chain']) + ')+1\n'
        source = ''.join(lines).replace('assert estimated136<1800,estimated136', 'assert estimated139<1800,estimated139')
        parent = json.loads((ROOT / 'reports/commercial61-native-136/overlay-result.json').read_text())
        anchor = "assert sha(esp/'commercial61-native-133/initrd.img')==" + repr(parent['shared_parent_overlay_sha256'])
        assert source.count(anchor) == 1
        source = source.replace(anchor, "assert sha(esp/'commercial61-native-136/initrd.img')==" + repr(overlay['shared_parent_overlay_sha256']), 1)
        source = source.replace('native board audio-BT module integration 136', 'native audio binding diagnostics 139')
    elif operation == 'retrieve-commercial-evidence':
        run = json.loads((ROOT / 'reports/commercial61-native-136/runtime-evidence/retrieval-manifest.json').read_text())['run']
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
        source = source139(operation)
        assert source == (REPORT / (operation + '.generated.py')).read_text()
        exec(compile(source, operation, 'exec'), {'__name__': '__main__', '__file__': str(BASE / (operation + '-139.py'))})
