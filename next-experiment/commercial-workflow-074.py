"""Retain every original guard and require tested YUV backends and parent chain."""
from pathlib import Path
import json
import runpy
import sys

b = Path(__file__).resolve().parent
previous = runpy.run_path(str(b / 'commercial-workflow-073.py'))
configure_local_transport = previous['configure_local_transport']


def source074(name):
    if name == 'install-commercial-native':
        admission = json.loads((b.parent / 'reports/commercial61-native-074/admission-test.json').read_text())
        assert all(admission[key] for key in ['tested_exact_backend_sources', 'exact_archive_delta',
            'original_service_identities_unchanged', 'original_codec_and_resources_unchanged',
            'protected_buffers_still_rejected', 'readonly_overlays', 'shared_parent_chain_verified'])
    source = previous['source073'](name)
    for before, after in [('commercial61-native-073', 'commercial61-native-074'),
        ('commercial-return-audit-073', 'commercial-return-audit-074'), ('COMMERCIAL073', 'COMMERCIAL074'),
        ('ordered_chain_equals_full_073', 'ordered_chain_equals_full_074'),
        ('retain-commercial-entries-073.py', 'retain-commercial-entries-074.py'),
        ('Public allocator requests 073', 'Linear YUV and BLOB backends 074')]:
        source = source.replace(before, after)
    if name == 'install-commercial-native':
        parent = json.loads((b.parent / 'reports/commercial61-native-073/overlay-result.json').read_text())
        old_parent = parent['shared_parent_overlay_sha256']
        anchor = "assert overlay_result['shared_parent_overlay_sha256']==" + repr(old_parent)
        assert source.count(anchor) == 1
        source = source.replace(anchor,
            "assert overlay_result['shared_parent_overlay_sha256']==" + repr(parent['sha256']), 1)
        old_chain = parent['chain'][:-1] + ['commercial61-native-074/initrd.img']
        anchor = "assert overlay_result['chain']==" + repr(old_chain)
        assert source.count(anchor) == 1
        source = source.replace(anchor,
            "assert overlay_result['chain']==" + repr(parent['chain'] + ['commercial61-native-074/initrd.img']), 1)
        anchor = "assert sha(esp/'commercial61-native-072/initrd.img')==" + repr(old_parent)
        assert source.count(anchor) == 1
        source = source.replace(anchor, anchor + "\nassert sha(esp/'commercial61-native-073/initrd.img')==" + repr(parent['sha256']), 1)
        anchor = "'initrd /commercial61-native-072/initrd.img','initrd /commercial61-native-074/initrd.img'"
        assert source.count(anchor) == 1
        source = source.replace(anchor,
            "'initrd /commercial61-native-072/initrd.img','initrd /commercial61-native-073/initrd.img','initrd /commercial61-native-074/initrd.img'", 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ['install-commercial-native', 'run-commercial-native',
                                               'retrieve-commercial-evidence', 'verify-commercial-return']
    configure_local_transport()
    exec(compile(source074(sys.argv[1]), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
