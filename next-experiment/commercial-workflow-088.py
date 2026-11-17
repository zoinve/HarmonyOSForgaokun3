"""New entry 088, retaining the byte-identical 087 core and its raw log labels."""
from pathlib import Path
import json
import runpy
import sys

BASE = Path(__file__).resolve().parent
previous = runpy.run_path(str(BASE / 'commercial-workflow-087.py'))
configure_local_transport = previous['configure_local_transport']


def source088(name):
    source = previous['source087'](name).replace('commercial61-native-087', 'commercial61-native-088').replace(
        'commercial-return-audit-087', 'commercial-return-audit-088').replace(
        'ordered_chain_equals_full_087', 'ordered_chain_equals_full_088').replace(
        'retain-commercial-entries-087.py', 'retain-commercial-entries-088.py').replace(
        'Original product workspace 087', 'SceneBoard canonical config view 088')
    if name == 'install-commercial-native':
        admission = json.loads((BASE.parent / 'reports/commercial61-native-088/admission-test.json').read_text())
        assert all(admission.values())
        parent = json.loads((BASE.parent / 'reports/commercial61-native-087/overlay-result.json').read_text())
        old = parent['shared_parent_overlay_sha256']
        replacements = {
            "assert overlay_result['shared_parent_overlay_sha256']==" + repr(old):
                "assert overlay_result['shared_parent_overlay_sha256']==" + repr(parent['sha256']),
            "assert overlay_result['chain']==" + repr(parent['chain'][:-1] + ['commercial61-native-088/initrd.img']):
                "assert overlay_result['chain']==" + repr(parent['chain'] + ['commercial61-native-088/initrd.img']),
            "assert sha(esp/'commercial61-native-086/initrd.img')==" + repr(old):
                "assert sha(esp/'commercial61-native-086/initrd.img')==" + repr(old) +
                "\nassert sha(esp/'commercial61-native-087/initrd.img')==" + repr(parent['sha256']),
            "'initrd /commercial61-native-086/initrd.img','initrd /commercial61-native-088/initrd.img'":
                "'initrd /commercial61-native-086/initrd.img','initrd /commercial61-native-087/initrd.img','initrd /commercial61-native-088/initrd.img'",
        }
        for anchor, replacement in replacements.items():
            assert source.count(anchor) == 1, anchor
            source = source.replace(anchor, replacement, 1)
        provenance = json.loads((BASE.parent / 'reports/commercial61-native-088/config-provenance.json').read_text())
        anchor = 'guards=[]'
        assert source.count(anchor) == 1
        dependency = '/home/zoinve/.local/share/harmony-arm64-kvm-lab/commercial61-native-087/bootstrap-runtime087'
        source = source.replace(anchor, 'assert sha(Path(' + repr(dependency) + '))==' +
                                repr(provenance['runtime_bootstrap_sha256']) + '\n' + anchor, 1)
    if name == 'retrieve-commercial-evidence':
        prior = json.loads((BASE.parent / 'reports/commercial61-native-087/runtime-evidence/retrieval-manifest.json').read_text())['run']
        anchor = "runs=list(mount.rglob('commercial61-native-088-*'));assert len(runs)==1,[str(p) for p in runs]"
        assert source.count(anchor) == 1
        source = source.replace(anchor,
            "runs=[p for p in mount.rglob('commercial61-native-087-*') if p.name != " + repr(prior) +
            "];assert len(runs)==1,[str(p) for p in runs]", 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ('install-commercial-native', 'run-commercial-native',
                                               'retrieve-commercial-evidence', 'verify-commercial-return')
    configure_local_transport()
    exec(compile(source088(sys.argv[1]), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
