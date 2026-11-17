from pathlib import Path
import json
import runpy
import sys

b = Path(__file__).resolve().parent
previous = runpy.run_path(str(b / 'commercial-workflow-085.py'))
configure_local_transport = previous['configure_local_transport']


def source086(name):
    source = previous['source085'](name).replace('commercial61-native-085', 'commercial61-native-086').replace(
        'commercial-return-audit-085', 'commercial-return-audit-086').replace('COMMERCIAL085', 'COMMERCIAL086').replace(
        'ordered_chain_equals_full_085', 'ordered_chain_equals_full_086').replace(
        'retain-commercial-entries-085.py', 'retain-commercial-entries-086.py').replace(
        'Native network and freeze probes 085', 'Native fault and UI layout 086')
    if name == 'install-commercial-native':
        admission = json.loads((b.parent / 'reports/commercial61-native-086/admission-test.json').read_text())
        assert all(admission.values())
        parent = json.loads((b.parent / 'reports/commercial61-native-085/overlay-result.json').read_text())
        old = parent['shared_parent_overlay_sha256']
        anchor = "assert overlay_result['shared_parent_overlay_sha256']==" + repr(old)
        assert source.count(anchor) == 1
        source = source.replace(anchor, "assert overlay_result['shared_parent_overlay_sha256']==" + repr(parent['sha256']), 1)
        anchor = "assert overlay_result['chain']==" + repr(parent['chain'][:-1] + ['commercial61-native-086/initrd.img'])
        assert source.count(anchor) == 1
        source = source.replace(anchor, "assert overlay_result['chain']==" + repr(parent['chain'] + ['commercial61-native-086/initrd.img']), 1)
        anchor = "assert sha(esp/'commercial61-native-084/initrd.img')==" + repr(old)
        assert source.count(anchor) == 1
        source = source.replace(anchor, anchor + "\nassert sha(esp/'commercial61-native-085/initrd.img')==" + repr(parent['sha256']), 1)
        anchor = "'initrd /commercial61-native-084/initrd.img','initrd /commercial61-native-086/initrd.img'"
        assert source.count(anchor) == 1
        source = source.replace(anchor, "'initrd /commercial61-native-084/initrd.img','initrd /commercial61-native-085/initrd.img','initrd /commercial61-native-086/initrd.img'", 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ['install-commercial-native', 'run-commercial-native',
                                               'retrieve-commercial-evidence', 'verify-commercial-return']
    configure_local_transport()
    exec(compile(source086(sys.argv[1]), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
