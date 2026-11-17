from pathlib import Path
import json
import runpy
import sys

b = Path(__file__).resolve().parent
previous = runpy.run_path(str(b / 'commercial-workflow-077.py'))
configure_local_transport = previous['configure_local_transport']


def source078(name):
    source = previous['source077'](name).replace('commercial61-native-077', 'commercial61-native-078').replace(
        'commercial-return-audit-077', 'commercial-return-audit-078').replace('COMMERCIAL077', 'COMMERCIAL078').replace(
        'ordered_chain_equals_full_077', 'ordered_chain_equals_full_078').replace(
        'retain-commercial-entries-077.py', 'retain-commercial-entries-078.py').replace(
        'Init managed desktop commands 076', 'Dock-ready desktop commands 078')
    if name == 'install-commercial-native':
        parent = json.loads((b.parent / 'reports/commercial61-native-077/overlay-result.json').read_text())
        old = parent['shared_parent_overlay_sha256']
        anchor = "assert overlay_result['shared_parent_overlay_sha256']==" + repr(old)
        assert source.count(anchor) == 1
        source = source.replace(anchor, "assert overlay_result['shared_parent_overlay_sha256']==" + repr(parent['sha256']), 1)
        anchor = "assert overlay_result['chain']==" + repr(parent['chain'][:-1] + ['commercial61-native-078/initrd.img'])
        assert source.count(anchor) == 1
        source = source.replace(anchor, "assert overlay_result['chain']==" + repr(parent['chain'] + ['commercial61-native-078/initrd.img']), 1)
        anchor = "assert sha(esp/'commercial61-native-076/initrd.img')==" + repr(old)
        assert source.count(anchor) == 1
        source = source.replace(anchor, anchor + "\nassert sha(esp/'commercial61-native-077/initrd.img')==" + repr(parent['sha256']), 1)
        anchor = "'initrd /commercial61-native-076/initrd.img','initrd /commercial61-native-078/initrd.img'"
        assert source.count(anchor) == 1
        source = source.replace(anchor, "'initrd /commercial61-native-076/initrd.img','initrd /commercial61-native-077/initrd.img','initrd /commercial61-native-078/initrd.img'", 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ['install-commercial-native', 'run-commercial-native',
                                               'retrieve-commercial-evidence', 'verify-commercial-return']
    configure_local_transport()
    exec(compile(source078(sys.argv[1]), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
