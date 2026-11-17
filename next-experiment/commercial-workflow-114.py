"""Inherit bounded native workflow, retaining parent 109 payload and runtime."""
from pathlib import Path
import json
import runpy
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
configure_local_transport = runpy.run_path(str(BASE / 'commercial-workflow-109.py'))['configure_local_transport']
OPERATIONS = ('install-commercial-native', 'run-commercial-native',
              'retrieve-commercial-evidence', 'verify-commercial-return')


def source114(name):
    assert name in OPERATIONS
    source = (ROOT / 'reports/commercial61-native-109' / (name + '.generated.py')).read_text()
    source = source.replace('commercial61-native-109', 'commercial61-native-114').replace(
        'commercial-return-audit-109', 'commercial-return-audit-114').replace(
        'ordered_chain_equals_full_109', 'ordered_chain_equals_full_114').replace(
        'Original memory service DFX and namespace 109', 'OOBE single startup owner 114')
    if name == 'install-commercial-native':
        parent = json.loads((ROOT / 'reports/commercial61-native-109/overlay-result.json').read_text())
        older = json.loads((ROOT / 'reports/commercial61-native-108/overlay-result.json').read_text())
        changes = {
            "assert overlay_result['shared_parent_overlay_sha256']==" + repr(older['sha256']):
                "assert overlay_result['shared_parent_overlay_sha256']==" + repr(parent['sha256']),
            "assert overlay_result['chain']==" + repr(parent['chain'][:-1] + ['commercial61-native-114/initrd.img']):
                "assert overlay_result['chain']==" + repr(parent['chain'] + ['commercial61-native-114/initrd.img']),
            "'initrd /commercial61-native-108/initrd.img','initrd /commercial61-native-114/initrd.img',options":
                "'initrd /commercial61-native-108/initrd.img','initrd /commercial61-native-109/initrd.img','initrd /commercial61-native-114/initrd.img',options",
            "assert sha(esp/'commercial61-native-108/initrd.img')==" + repr(older['sha256']):
                "assert sha(esp/'commercial61-native-108/initrd.img')==" + repr(older['sha256']) +
                "\nassert sha(esp/'commercial61-native-109/initrd.img')==" + repr(parent['sha256']),
        }
        for old, new in changes.items():
            assert source.count(old) == 1, old
            source = source.replace(old, new, 1)
    if name == 'retrieve-commercial-evidence':
        previous = json.loads((ROOT / 'reports/commercial61-native-109/runtime-evidence/retrieval-manifest.json').read_text())['run']
        anchor = 'if p.name not in ['
        assert source.count(anchor) == 1
        source = source.replace(anchor, anchor + repr(previous) + ', ', 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in OPERATIONS
    report = ROOT / 'reports/commercial61-native-114'
    assert all(json.loads((report / 'admission-test.json').read_text()).values())
    operation = sys.argv[1]
    source = source114(operation)
    assert source == (report / (operation + '.generated.py')).read_text()
    configure_local_transport()
    exec(compile(source, str(BASE / (operation + '-114.py')), 'exec'),
         {'__name__': '__main__', '__file__': str(BASE / (operation + '-114.py'))})
