"""Require the exact 072 shared parent before the new incremental overlay."""
from pathlib import Path
import json
import runpy
import sys

b = Path(__file__).resolve().parent
previous = runpy.run_path(str(b / 'commercial-workflow-072.py'))
configure_local_transport = previous['configure_local_transport']


def source073(name):
    if name == 'install-commercial-native':
        test = json.loads((b.parent / 'reports/commercial61-native-073/admission-test.json').read_text())
        assert all(test[key] for key in ['exact_observer_source_delta',
            'all_other_existing_archive_members_unchanged', 'original_software_backend_unchanged',
            'original_resource_files_unchanged', 'allocator_public_logging_only',
            'allocator_return_values_unchanged', 'original_service_identities_unchanged',
            'compiled_logger_tests_passed', 'shared_parent_chain_verified', 'readonly_overlays'])
    return transform073(previous['source072'](name), name)


def transform073(source, name):
    for before, after in [('commercial61-native-072', 'commercial61-native-073'),
        ('commercial-return-audit-072', 'commercial-return-audit-073'), ('COMMERCIAL072', 'COMMERCIAL073'),
        ('ordered_chain_equals_full_072', 'ordered_chain_equals_full_073'),
        ('retain-commercial-entries-072.py', 'retain-commercial-entries-073.py'),
        ('Real software codec backend 072', 'Public allocator requests 073')]:
        source = source.replace(before, after)
    if name == 'install-commercial-native':
        parent = json.loads((b.parent / 'reports/commercial61-native-072/overlay-result-xz.json').read_text())
        archive_anchor = "assert hashlib.sha256(overlay).hexdigest()==overlay_result['sha256']"
        assert source.count(archive_anchor) == 1
        chain = ['commercial61-native-001/initrd.img', 'commercial61-native-017/initrd.img',
                 'commercial61-native-016/initrd.img', 'commercial61-native-072/initrd.img',
                 'commercial61-native-073/initrd.img']
        source = source.replace(archive_anchor, archive_anchor +
            "\nassert overlay_result['ordered_chain_equals_full_073']" +
            "\nassert overlay_result['chain']==" + repr(chain) +
            "\nassert overlay_result['shared_parent_overlay_sha256']==" + repr(parent['sha256']), 1)
        anchor = "assert sha(esp/'commercial61-native-017/initrd.img')=='6e806d98c1ffa385a9869da996439d4d44e4601d859c0d754c95c4e57d6651c7'"
        assert source.count(anchor) == 1
        source = source.replace(anchor, anchor + "\nassert sha(esp/'commercial61-native-072/initrd.img')==" + repr(parent['sha256']), 1)
        anchor = "'initrd /commercial61-native-016/initrd.img','initrd /commercial61-native-073/initrd.img'"
        assert source.count(anchor) == 1
        source = source.replace(anchor,
            "'initrd /commercial61-native-016/initrd.img','initrd /commercial61-native-072/initrd.img','initrd /commercial61-native-073/initrd.img'", 1)
        assert "'initrd /commercial61-native-072/initrd.img','initrd /commercial61-native-073/initrd.img'" in source
    return source


if __name__ == '__main__':
    allowed = ['install-commercial-native', 'run-commercial-native',
               'retrieve-commercial-evidence', 'verify-commercial-return']
    assert len(sys.argv) == 2 and sys.argv[1] in allowed
    configure_local_transport()
    exec(compile(source073(sys.argv[1]), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
