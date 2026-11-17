from pathlib import Path
import json
import runpy
import sys

b = Path(__file__).resolve().parent
previous = runpy.run_path(str(b / 'commercial-workflow-079.py'))
configure_local_transport = previous['configure_local_transport']


def source080(name):
    source = previous['source079'](name).replace('commercial61-native-079', 'commercial61-native-080').replace(
        'commercial-return-audit-079', 'commercial-return-audit-080').replace('COMMERCIAL079', 'COMMERCIAL080').replace(
        'ordered_chain_equals_full_079', 'ordered_chain_equals_full_080').replace(
        'retain-commercial-entries-079.py', 'retain-commercial-entries-080.py').replace(
        'Native Wi-Fi firmware observation 079', 'Native Wi-Fi power dependencies 080')
    if name == 'install-commercial-native':
        admission = json.loads((b.parent / 'reports/commercial61-native-080/admission-test.json').read_text())
        assert all(admission.values())
        parent = json.loads((b.parent / 'reports/commercial61-native-079/overlay-result.json').read_text())
        old = parent['shared_parent_overlay_sha256']
        anchor = "assert overlay_result['shared_parent_overlay_sha256']==" + repr(old)
        assert source.count(anchor) == 1
        source = source.replace(anchor, "assert overlay_result['shared_parent_overlay_sha256']==" + repr(parent['sha256']), 1)
        anchor = "assert overlay_result['chain']==" + repr(parent['chain'][:-1] + ['commercial61-native-080/initrd.img'])
        assert source.count(anchor) == 1
        source = source.replace(anchor, "assert overlay_result['chain']==" + repr(parent['chain'] + ['commercial61-native-080/initrd.img']), 1)
        anchor = "assert sha(esp/'commercial61-native-078/initrd.img')==" + repr(old)
        assert source.count(anchor) == 1
        source = source.replace(anchor, anchor + "\nassert sha(esp/'commercial61-native-079/initrd.img')==" + repr(parent['sha256']), 1)
        anchor = "'initrd /commercial61-native-078/initrd.img','initrd /commercial61-native-080/initrd.img'"
        assert source.count(anchor) == 1
        source = source.replace(anchor, "'initrd /commercial61-native-078/initrd.img','initrd /commercial61-native-079/initrd.img','initrd /commercial61-native-080/initrd.img'", 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ['install-commercial-native', 'run-commercial-native',
                                               'retrieve-commercial-evidence', 'verify-commercial-return']
    configure_local_transport()
    exec(compile(source080(sys.argv[1]), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
