"""Keep the inherited one-boot, retrieval and preservation gates for 108."""
from pathlib import Path
import json
import runpy
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
configure_local_transport = runpy.run_path(str(BASE / 'commercial-workflow-107.py'))['configure_local_transport']


def source108(name):
    source = (ROOT / 'reports/commercial61-native-107' / (name + '.generated.py')).read_text()
    source = source.replace('commercial61-native-107', 'commercial61-native-108').replace(
        'commercial-return-audit-107', 'commercial-return-audit-108').replace(
        'ordered_chain_equals_full_107', 'ordered_chain_equals_full_108').replace(
        'Original query event two-service DFX 107', 'Original memory wrapper directory prerequisites 108')
    if name == 'install-commercial-native':
        assert all(json.loads((ROOT / 'reports/commercial61-native-108/admission-test.json').read_text()).values())
        parent = json.loads((ROOT / 'reports/commercial61-native-107/overlay-result.json').read_text())
        older = json.loads((ROOT / 'reports/commercial61-native-105/overlay-result.json').read_text())
        result = json.loads((ROOT / 'reports/commercial61-native-108/result.json').read_text())
        metadata = result['memmgr108']
        changes = {
            "assert overlay_result['shared_parent_overlay_sha256']==" + repr(older['sha256']):
                "assert overlay_result['shared_parent_overlay_sha256']==" + repr(parent['sha256']),
            "assert overlay_result['chain']==" + repr(older['chain'] + ['commercial61-native-108/initrd.img']):
                "assert overlay_result['chain']==" + repr(parent['chain'] + ['commercial61-native-108/initrd.img']),
            "'initrd /commercial61-native-105/initrd.img','initrd /commercial61-native-108/initrd.img',options":
                "'initrd /commercial61-native-105/initrd.img','initrd /commercial61-native-107/initrd.img','initrd /commercial61-native-108/initrd.img',options",
            "assert sha(esp/'commercial61-native-105/initrd.img')==" + repr(older['sha256']):
                "assert sha(esp/'commercial61-native-105/initrd.img')==" + repr(older['sha256']) +
                "\nassert sha(esp/'commercial61-native-107/initrd.img')==" + repr(parent['sha256']),
            "assert sha(root/'bootstrap-runtime087')==" + repr(metadata['old_runtime_sha256']):
                "assert sha(root/'bootstrap-runtime087')==" + repr(metadata['runtime_sha256']),
        }
        for old, new in changes.items():
            assert source.count(old) == 1, old
            source = source.replace(old, new, 1)
    if name == 'retrieve-commercial-evidence':
        previous = json.loads((ROOT / 'reports/commercial61-native-107/runtime-evidence/retrieval-manifest.json').read_text())['run']
        anchor = 'if p.name not in ['
        assert source.count(anchor) == 1
        source = source.replace(anchor, anchor + repr(previous) + ', ', 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ('install-commercial-native', 'run-commercial-native',
                                               'retrieve-commercial-evidence', 'verify-commercial-return')
    configure_local_transport()
    exec(compile(source108(sys.argv[1]), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
