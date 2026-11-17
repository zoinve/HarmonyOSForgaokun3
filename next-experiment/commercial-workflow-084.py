from pathlib import Path
import json
import runpy
import sys

b = Path(__file__).resolve().parent
previous = runpy.run_path(str(b / 'commercial-workflow-083.py'))
configure_local_transport = previous['configure_local_transport']


def source084(name):
    source = previous['source083'](name).replace('commercial61-native-083', 'commercial61-native-084').replace(
        'commercial-return-audit-083', 'commercial-return-audit-084').replace('COMMERCIAL083', 'COMMERCIAL084').replace(
        'ordered_chain_equals_full_083', 'ordered_chain_equals_full_084').replace(
        'retain-commercial-entries-083.py', 'retain-commercial-entries-084.py').replace(
        'Native supplicant scan 083', 'Native Wi-Fi association 084')
    if name == 'install-commercial-native':
        admission = json.loads((b.parent / 'reports/commercial61-native-084/admission-test.json').read_text())
        assert all(admission.values())
        parent = json.loads((b.parent / 'reports/commercial61-native-083/overlay-result.json').read_text())
        old = parent['shared_parent_overlay_sha256']
        anchor = "assert overlay_result['shared_parent_overlay_sha256']==" + repr(old)
        assert source.count(anchor) == 1
        source = source.replace(anchor, "assert overlay_result['shared_parent_overlay_sha256']==" + repr(parent['sha256']), 1)
        anchor = "assert overlay_result['chain']==" + repr(parent['chain'][:-1] + ['commercial61-native-084/initrd.img'])
        assert source.count(anchor) == 1
        source = source.replace(anchor, "assert overlay_result['chain']==" + repr(parent['chain'] + ['commercial61-native-084/initrd.img']), 1)
        anchor = "assert sha(esp/'commercial61-native-082/initrd.img')==" + repr(old)
        assert source.count(anchor) == 1
        source = source.replace(anchor, anchor + "\nassert sha(esp/'commercial61-native-083/initrd.img')==" + repr(parent['sha256']), 1)
        anchor = "'initrd /commercial61-native-082/initrd.img','initrd /commercial61-native-084/initrd.img'"
        assert source.count(anchor) == 1
        source = source.replace(anchor, "'initrd /commercial61-native-082/initrd.img','initrd /commercial61-native-083/initrd.img','initrd /commercial61-native-084/initrd.img'", 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ['install-commercial-native', 'run-commercial-native',
                                               'retrieve-commercial-evidence', 'verify-commercial-return']
    configure_local_transport()
    exec(compile(source084(sys.argv[1]), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
