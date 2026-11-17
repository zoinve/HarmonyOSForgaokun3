from pathlib import Path
import json
import runpy
import sys

b = Path(__file__).resolve().parent
previous = runpy.run_path(str(b / 'commercial-workflow-075.py'))
configure_local_transport = previous['configure_local_transport']


def source076(name):
    if name == 'install-commercial-native':
        admission = json.loads((b.parent / 'reports/commercial61-native-076/admission-test.json').read_text())
        assert all(admission[key] for key in ['exact_archive_delta', 'original_service_definitions_preserved',
            'distinct_init_managed_service', 'no_supplied_token_or_activation_state', 'shared_parent_chain_verified'])
    source = previous['source075'](name)
    for old, new in [('commercial61-native-075', 'commercial61-native-076'),
        ('commercial-return-audit-075', 'commercial-return-audit-076'), ('COMMERCIAL075', 'COMMERCIAL076'),
        ('ordered_chain_equals_full_075', 'ordered_chain_equals_full_076'),
        ('retain-commercial-entries-075.py', 'retain-commercial-entries-076.py'),
        ('Reference direct desktop 075', 'Init managed desktop commands 076')]:
        source = source.replace(old, new)
    if name == 'install-commercial-native':
        parent = json.loads((b.parent / 'reports/commercial61-native-075/overlay-result.json').read_text())
        old = parent['shared_parent_overlay_sha256']
        anchor = "assert overlay_result['shared_parent_overlay_sha256']==" + repr(old)
        assert source.count(anchor) == 1
        source = source.replace(anchor, "assert overlay_result['shared_parent_overlay_sha256']==" + repr(parent['sha256']), 1)
        anchor = "assert overlay_result['chain']==" + repr(parent['chain'][:-1] + ['commercial61-native-076/initrd.img'])
        assert source.count(anchor) == 1
        source = source.replace(anchor, "assert overlay_result['chain']==" + repr(parent['chain'] + ['commercial61-native-076/initrd.img']), 1)
        anchor = "assert sha(esp/'commercial61-native-074/initrd.img')==" + repr(old)
        assert source.count(anchor) == 1
        source = source.replace(anchor, anchor + "\nassert sha(esp/'commercial61-native-075/initrd.img')==" + repr(parent['sha256']), 1)
        anchor = "'initrd /commercial61-native-074/initrd.img','initrd /commercial61-native-076/initrd.img'"
        assert source.count(anchor) == 1
        source = source.replace(anchor, "'initrd /commercial61-native-074/initrd.img','initrd /commercial61-native-075/initrd.img','initrd /commercial61-native-076/initrd.img'", 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ['install-commercial-native', 'run-commercial-native',
                                               'retrieve-commercial-evidence', 'verify-commercial-return']
    configure_local_transport()
    exec(compile(source076(sys.argv[1]), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
