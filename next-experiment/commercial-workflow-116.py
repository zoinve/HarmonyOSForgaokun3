"""Bounded checkpoint-gated Home workflow, with parent 114 preserved."""
from pathlib import Path
import json
import runpy
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
PREVIOUS = runpy.run_path(str(BASE / 'commercial-workflow-114.py'))
configure_local_transport = PREVIOUS['configure_local_transport']
OPERATIONS = PREVIOUS['OPERATIONS']


def source116(name):
    assert name in OPERATIONS
    source = (ROOT / 'reports/commercial61-native-114' / (name + '.generated.py')).read_text()
    source = source.replace('commercial61-native-114', 'commercial61-native-116').replace(
        'commercial-return-audit-114', 'commercial-return-audit-116').replace(
        'ordered_chain_equals_full_114', 'ordered_chain_equals_full_116').replace(
        'OOBE single startup owner 114', 'OOBE original collaboration checkpoint 116')
    if name == 'install-commercial-native':
        parent = json.loads((ROOT / 'reports/commercial61-native-114/overlay-result.json').read_text())
        older = json.loads((ROOT / 'reports/commercial61-native-109/overlay-result.json').read_text())
        changes = {
            "assert overlay_result['shared_parent_overlay_sha256']==" + repr(older['sha256']):
                "assert overlay_result['shared_parent_overlay_sha256']==" + repr(parent['sha256']),
            "assert overlay_result['chain']==" + repr(parent['chain'][:-1] + ['commercial61-native-116/initrd.img']):
                "assert overlay_result['chain']==" + repr(parent['chain'] + ['commercial61-native-116/initrd.img']),
            "'initrd /commercial61-native-109/initrd.img','initrd /commercial61-native-116/initrd.img',options":
                "'initrd /commercial61-native-109/initrd.img','initrd /commercial61-native-114/initrd.img','initrd /commercial61-native-116/initrd.img',options",
            "assert sha(esp/'commercial61-native-109/initrd.img')==" + repr(older['sha256']):
                "assert sha(esp/'commercial61-native-109/initrd.img')==" + repr(older['sha256']) +
                "\nassert sha(esp/'commercial61-native-114/initrd.img')==" + repr(parent['sha256']),
        }
        for old, new in changes.items():
            assert source.count(old) == 1, old
            source = source.replace(old, new, 1)
    if name == 'retrieve-commercial-evidence':
        previous = json.loads((ROOT / 'reports/commercial61-native-114/runtime-evidence/retrieval-manifest.json').read_text())['run']
        anchor = 'if p.name not in ['
        assert source.count(anchor) == 1
        source = source.replace(anchor, anchor + repr(previous) + ', ', 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in OPERATIONS
    report = ROOT / 'reports/commercial61-native-116'
    assert all(json.loads((report / 'admission-test.json').read_text()).values())
    operation = sys.argv[1]
    source = source116(operation)
    assert source == (report / (operation + '.generated.py')).read_text()
    configure_local_transport()
    exec(compile(source, str(BASE / (operation + '-116.py')), 'exec'),
         {'__name__': '__main__', '__file__': str(BASE / (operation + '-116.py'))})
