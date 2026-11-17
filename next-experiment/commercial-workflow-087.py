from pathlib import Path
import json
import runpy
import sys

base = Path(__file__).resolve().parent
previous = runpy.run_path(str(base / 'commercial-workflow-086.py'))
configure_local_transport = previous['configure_local_transport']


def source087(name):
    source = previous['source086'](name).replace('commercial61-native-086', 'commercial61-native-087').replace(
        'commercial-return-audit-086', 'commercial-return-audit-087').replace('COMMERCIAL086', 'COMMERCIAL087').replace(
        'ordered_chain_equals_full_086', 'ordered_chain_equals_full_087').replace(
        'retain-commercial-entries-086.py', 'retain-commercial-entries-087.py').replace(
        'Native fault and UI layout 086', 'Original product workspace 087')
    if name == 'install-commercial-native':
        admission = json.loads((base.parent / 'reports/commercial61-native-087/admission-test.json').read_text())
        assert all(admission.values())
        parent = json.loads((base.parent / 'reports/commercial61-native-086/overlay-result.json').read_text())
        old = parent['shared_parent_overlay_sha256']
        replacements = {
            "assert overlay_result['shared_parent_overlay_sha256']==" + repr(old):
                "assert overlay_result['shared_parent_overlay_sha256']==" + repr(parent['sha256']),
            "assert overlay_result['chain']==" + repr(parent['chain'][:-1] + ['commercial61-native-087/initrd.img']):
                "assert overlay_result['chain']==" + repr(parent['chain'] + ['commercial61-native-087/initrd.img']),
            "assert sha(esp/'commercial61-native-085/initrd.img')==" + repr(old):
                "assert sha(esp/'commercial61-native-085/initrd.img')==" + repr(old) +
                "\nassert sha(esp/'commercial61-native-086/initrd.img')==" + repr(parent['sha256']),
            "'initrd /commercial61-native-085/initrd.img','initrd /commercial61-native-087/initrd.img'":
                "'initrd /commercial61-native-085/initrd.img','initrd /commercial61-native-086/initrd.img','initrd /commercial61-native-087/initrd.img'",
            "if item['name'] in ['init','bootstrap']:":
                "if item['name'] in ['init','bootstrap','bootstrap-runtime087']:",
            "for n in ['init','bootstrap']:":
                "for n in ['init','bootstrap','bootstrap-runtime087']:",
        }
        for anchor, replacement in replacements.items():
            assert source.count(anchor) == 1, anchor
            source = source.replace(anchor, replacement, 1)
        provenance = json.loads((base.parent / 'reports/commercial61-native-087/workspace-provenance.json').read_text())
        anchor = 'guards=[]'
        assert source.count(anchor) == 1
        source = source.replace(anchor,
            "assert sha(root/'bootstrap-runtime087')==" + repr(provenance['runtime_bootstrap_sha256']) + '\n' + anchor, 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ('install-commercial-native', 'run-commercial-native',
                                               'retrieve-commercial-evidence', 'verify-commercial-return')
    configure_local_transport()
    exec(compile(source087(sys.argv[1]), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
