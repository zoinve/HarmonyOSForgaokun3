"""Inherit completed transport, one-boot and preservation gates from 105."""
from pathlib import Path
import json
import runpy
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
configure_local_transport = runpy.run_path(str(BASE / 'commercial-workflow-105.py'))['configure_local_transport']


def source107(name):
    source = (ROOT / 'reports/commercial61-native-105' / (name + '.generated.py')).read_text()
    source = source.replace('commercial61-native-105', 'commercial61-native-107').replace(
        'commercial-return-audit-105', 'commercial-return-audit-107').replace(
        'ordered_chain_equals_full_105', 'ordered_chain_equals_full_107').replace(
        'Original DFX before proc survey 105', 'Original query event two-service DFX 107')
    if name == 'install-commercial-native':
        assert all(json.loads((ROOT / 'reports/commercial61-native-107/admission-test.json').read_text()).values())
        parent = json.loads((ROOT / 'reports/commercial61-native-105/overlay-result.json').read_text())
        older = json.loads((ROOT / 'reports/commercial61-native-104/overlay-result.json').read_text())
        changes = {
            "assert overlay_result['shared_parent_overlay_sha256']==" + repr(older['sha256']):
                "assert overlay_result['shared_parent_overlay_sha256']==" + repr(parent['sha256']),
            "assert overlay_result['chain']==" + repr(older['chain'] + ['commercial61-native-107/initrd.img']):
                "assert overlay_result['chain']==" + repr(parent['chain'] + ['commercial61-native-107/initrd.img']),
            "'initrd /commercial61-native-104/initrd.img','initrd /commercial61-native-107/initrd.img',options":
                "'initrd /commercial61-native-104/initrd.img','initrd /commercial61-native-105/initrd.img','initrd /commercial61-native-107/initrd.img',options",
            "assert sha(esp/'commercial61-native-104/initrd.img')==" + repr(older['sha256']):
                "assert sha(esp/'commercial61-native-104/initrd.img')==" + repr(older['sha256']) +
                "\nassert sha(esp/'commercial61-native-105/initrd.img')==" + repr(parent['sha256']),
        }
        for old, new in changes.items():
            assert source.count(old) == 1, old
            source = source.replace(old, new, 1)
    if name == 'retrieve-commercial-evidence':
        previous = json.loads((ROOT / 'reports/commercial61-native-105/runtime-evidence/retrieval-manifest.json').read_text())['run']
        anchor = 'if p.name not in ['
        assert source.count(anchor) == 1
        source = source.replace(anchor, anchor + repr(previous) + ', ', 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ('install-commercial-native', 'run-commercial-native',
                                               'retrieve-commercial-evidence', 'verify-commercial-return')
    configure_local_transport()
    exec(compile(source107(sys.argv[1]), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
