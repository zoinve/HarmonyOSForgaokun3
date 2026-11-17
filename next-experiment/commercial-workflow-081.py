from pathlib import Path
import json
import runpy
import sys

b = Path(__file__).resolve().parent
previous = runpy.run_path(str(b / 'commercial-workflow-080.py'))
configure_local_transport = previous['configure_local_transport']


def source081(name):
    source = previous['source080'](name).replace('commercial61-native-080', 'commercial61-native-081').replace(
        'commercial-return-audit-080', 'commercial-return-audit-081').replace('COMMERCIAL080', 'COMMERCIAL081').replace(
        'ordered_chain_equals_full_080', 'ordered_chain_equals_full_081').replace(
        'retain-commercial-entries-080.py', 'retain-commercial-entries-081.py').replace(
        'Native Wi-Fi power dependencies 080', 'Native Wi-Fi QRTR transport 081')
    if name == 'install-commercial-native':
        admission = json.loads((b.parent / 'reports/commercial61-native-081/admission-test.json').read_text())
        assert all(admission.values())
        parent = json.loads((b.parent / 'reports/commercial61-native-080/overlay-result.json').read_text())
        old = parent['shared_parent_overlay_sha256']
        anchor = "assert overlay_result['shared_parent_overlay_sha256']==" + repr(old)
        assert source.count(anchor) == 1
        source = source.replace(anchor, "assert overlay_result['shared_parent_overlay_sha256']==" + repr(parent['sha256']), 1)
        anchor = "assert overlay_result['chain']==" + repr(parent['chain'][:-1] + ['commercial61-native-081/initrd.img'])
        assert source.count(anchor) == 1
        source = source.replace(anchor, "assert overlay_result['chain']==" + repr(parent['chain'] + ['commercial61-native-081/initrd.img']), 1)
        anchor = "assert sha(esp/'commercial61-native-079/initrd.img')==" + repr(old)
        assert source.count(anchor) == 1
        source = source.replace(anchor, anchor + "\nassert sha(esp/'commercial61-native-080/initrd.img')==" + repr(parent['sha256']), 1)
        anchor = "'initrd /commercial61-native-079/initrd.img','initrd /commercial61-native-081/initrd.img'"
        assert source.count(anchor) == 1
        source = source.replace(anchor, "'initrd /commercial61-native-079/initrd.img','initrd /commercial61-native-080/initrd.img','initrd /commercial61-native-081/initrd.img'", 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ['install-commercial-native', 'run-commercial-native',
                                               'retrieve-commercial-evidence', 'verify-commercial-return']
    configure_local_transport()
    exec(compile(source081(sys.argv[1]), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
