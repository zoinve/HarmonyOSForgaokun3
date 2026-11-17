from pathlib import Path
import json
import runpy
import sys

b = Path(__file__).resolve().parent
previous = runpy.run_path(str(b / 'commercial-workflow-070.py'))
configure_local_transport = previous['configure_local_transport']


def source072(name):
    if name == 'install-commercial-native':
        test = json.loads((b.parent / 'reports/commercial61-native-072/admission-test.json').read_text())
        assert all(test[k] for k in ['exact_ram_source_delta',
            'all_original_members_unchanged_except_init_bootstrap', 'original_resource_files_unchanged',
            'original_adapter_files_unchanged', 'original_init_service_definitions_unchanged',
            'real_isolated_decode_passed', 'helper_sanitizer_tests_passed', 'exact_peer_uid_guard',
            'readonly_overlay', 'no_original_authentication_changes', 'no_private_abi_hooks'])
    source = previous['source070'](name)
    for before, after in [('commercial61-native-070', 'commercial61-native-072'),
        ('commercial-return-audit-070', 'commercial-return-audit-072'), ('COMMERCIAL070', 'COMMERCIAL072'),
        ('ordered_chain_equals_full_070', 'ordered_chain_equals_full_072'),
        ('retain-commercial-entries-070.py', 'retain-commercial-entries-072.py'),
        ('Original HAP rawfile layout 070', 'Real software codec backend 072')]:
        source = source.replace(before, after)
    return source


if __name__ == '__main__':
    allowed = ['install-commercial-native', 'run-commercial-native',
               'retrieve-commercial-evidence', 'verify-commercial-return']
    assert len(sys.argv) == 2 and sys.argv[1] in allowed
    configure_local_transport()
    exec(compile(source072(sys.argv[1]), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
