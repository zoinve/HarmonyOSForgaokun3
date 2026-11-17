"""Boot with prepared first-run flags; keep all original authentication paths."""
from pathlib import Path
import json
import runpy
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
PREVIOUS = runpy.run_path(str(BASE / 'commercial-workflow-121.py'))
configure_local_transport = PREVIOUS['configure_local_transport']
OPERATIONS = PREVIOUS['OPERATIONS']


def source123(name):
    assert name in OPERATIONS
    source = (ROOT / 'reports/commercial61-native-121' / (name + '.generated.py')).read_text()
    source = source.replace('commercial61-native-121', 'commercial61-native-123').replace(
        'commercial-return-audit-121', 'commercial-return-audit-123').replace(
        'ordered_chain_equals_full_121', 'ordered_chain_equals_full_123').replace(
        'OOBE private offline data capture 121', 'OOBE original-schema development seed 123')
    if name == 'install-commercial-native':
        parent = json.loads((ROOT / 'reports/commercial61-native-121/overlay-result.json').read_text())
        changes = {
            "assert overlay_result['shared_parent_overlay_sha256']==" + repr(parent['shared_parent_overlay_sha256']):
                "assert overlay_result['shared_parent_overlay_sha256']==" + repr(parent['sha256']),
            "assert overlay_result['chain']==" + repr(parent['chain'][:-1] + ['commercial61-native-123/initrd.img']):
                "assert overlay_result['chain']==" + repr(parent['chain'] + ['commercial61-native-123/initrd.img']),
            "'initrd /commercial61-native-116/initrd.img','initrd /commercial61-native-123/initrd.img',options":
                "'initrd /commercial61-native-116/initrd.img','initrd /commercial61-native-121/initrd.img','initrd /commercial61-native-123/initrd.img',options",
            "assert sha(esp/'commercial61-native-116/initrd.img')==" + repr(parent['shared_parent_overlay_sha256']):
                "assert sha(esp/'commercial61-native-116/initrd.img')==" + repr(parent['shared_parent_overlay_sha256']) +
                "\nassert sha(esp/'commercial61-native-121/initrd.img')==" + repr(parent['sha256']),
        }
        for old, new in changes.items():
            assert source.count(old) == 1, old
            source = source.replace(old, new, 1)
        obsolete = "\nassert not Path('/mnt/lab/private-oobe121').exists()"
        assert source.count(obsolete) == 1
        source = source.replace(obsolete, '', 1)
        seed = json.loads((ROOT / 'reports/oobe-seed-preparation-123/result.json').read_text())
        anchor = "assert sha(root/'bootstrap-runtime087')=="
        assert source.count(anchor) == 1
        check = ('seed123=Path(' + repr(seed['seed_path']) + ')\n' +
            'assert seed123.is_file() and not seed123.is_symlink() and seed123.stat().st_size==536870912\n' +
            'assert sha(seed123)==' + repr(seed['seed_sha256']) + '\n')
        source = source.replace(anchor, check + anchor, 1)
    if name == 'retrieve-commercial-evidence':
        previous = json.loads((ROOT / 'reports/commercial61-native-121/runtime-evidence/retrieval-manifest.json').read_text())['run']
        anchor = 'if p.name not in ['
        assert source.count(anchor) == 1
        source = source.replace(anchor, anchor + repr(previous) + ', ', 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in OPERATIONS
    report = ROOT / 'reports/commercial61-native-123'
    assert all(json.loads((report / 'admission-test.json').read_text()).values())
    operation = sys.argv[1]
    source = source123(operation)
    assert source == (report / (operation + '.generated.py')).read_text()
    configure_local_transport()
    exec(compile(source, str(BASE / (operation + '-123.py')), 'exec'),
         {'__name__': '__main__', '__file__': str(BASE / (operation + '-123.py'))})
