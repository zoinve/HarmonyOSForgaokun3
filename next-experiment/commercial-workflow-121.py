"""Bounded snapshot-only boot, with original 116 runtime and private target data."""
from pathlib import Path
import json
import runpy
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
PREVIOUS = runpy.run_path(str(BASE / 'commercial-workflow-116.py'))
configure_local_transport = PREVIOUS['configure_local_transport']
OPERATIONS = PREVIOUS['OPERATIONS']


def source121(name):
    assert name in OPERATIONS
    source = (ROOT / 'reports/commercial61-native-116' / (name + '.generated.py')).read_text()
    source = source.replace('commercial61-native-116', 'commercial61-native-121').replace(
        'commercial-return-audit-116', 'commercial-return-audit-121').replace(
        'ordered_chain_equals_full_116', 'ordered_chain_equals_full_121').replace(
        'OOBE original collaboration checkpoint 116', 'OOBE private offline data capture 121')
    if name == 'install-commercial-native':
        parent = json.loads((ROOT / 'reports/commercial61-native-116/overlay-result.json').read_text())
        changes = {
            "assert overlay_result['shared_parent_overlay_sha256']==" + repr(parent['shared_parent_overlay_sha256']):
                "assert overlay_result['shared_parent_overlay_sha256']==" + repr(parent['sha256']),
            "assert overlay_result['chain']==" + repr(parent['chain'][:-1] + ['commercial61-native-121/initrd.img']):
                "assert overlay_result['chain']==" + repr(parent['chain'] + ['commercial61-native-121/initrd.img']),
            "'initrd /commercial61-native-114/initrd.img','initrd /commercial61-native-121/initrd.img',options":
                "'initrd /commercial61-native-114/initrd.img','initrd /commercial61-native-116/initrd.img','initrd /commercial61-native-121/initrd.img',options",
            "assert sha(esp/'commercial61-native-114/initrd.img')==" + repr(parent['shared_parent_overlay_sha256']):
                "assert sha(esp/'commercial61-native-114/initrd.img')==" + repr(parent['shared_parent_overlay_sha256']) +
                "\nassert sha(esp/'commercial61-native-116/initrd.img')==" + repr(parent['sha256']),
        }
        for old, new in changes.items():
            assert source.count(old) == 1, old
            source = source.replace(old, new, 1)
        anchor = "assert not root.exists();root.mkdir()"
        assert source.count(anchor) == 1
        source = source.replace(anchor, "assert not root.exists();root.mkdir()\nassert not Path('/mnt/lab/private-oobe121').exists()", 1)
    if name == 'retrieve-commercial-evidence':
        previous = json.loads((ROOT / 'reports/commercial61-native-116/runtime-evidence/retrieval-manifest.json').read_text())['run']
        anchor = 'if p.name not in ['
        assert source.count(anchor) == 1
        source = source.replace(anchor, anchor + repr(previous) + ', ', 1)
        # Private disk is outside the evidence run directory and is never archived.
        anchor = "run=runs[0]"
        assert source.count(anchor) == 1
        source = source.replace(anchor, anchor + "\n assert run.parent != mount/'private-oobe121'\n assert not any(p.is_dir() for p in run.iterdir()), 'unexpected subdirectory; refusing recursive export'", 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in OPERATIONS
    report = ROOT / 'reports/commercial61-native-121'
    assert all(json.loads((report / 'admission-test.json').read_text()).values())
    operation = sys.argv[1]
    source = source121(operation)
    assert source == (report / (operation + '.generated.py')).read_text()
    configure_local_transport()
    exec(compile(source, str(BASE / (operation + '-121.py')), 'exec'),
         {'__name__': '__main__', '__file__': str(BASE / (operation + '-121.py'))})
