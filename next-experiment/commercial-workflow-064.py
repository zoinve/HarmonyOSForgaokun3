from pathlib import Path
import json
import runpy

b = Path(__file__).resolve().parent
previous = runpy.run_path(str(b / 'commercial-workflow-063.py'))
configure_local_transport = previous['configure_local_transport']


def source064(name):
    if name == 'install-commercial-native':
        test = json.loads((b.parent / 'reports/commercial61-native-064/hwbreak-test-revision2.json').read_text())
        assert test['public_event_diagnostics_tested']
        assert test['exact_delta_from_063'] == ['init', 'native-target/desktop-order020.sh']
        for key in ['synthetic_ring_tests_passed', 'executable_memory_tests_passed',
                    'modules_byte_identical_to_045', 'original_bootstrap_byte_identical',
                    'original_userland_binaries_byte_identical', 'account_order_tests_passed']:
            assert test[key], key
    source = previous['source063'](name)
    for before, after in [('commercial61-native-063', 'commercial61-native-064'),
                          ('commercial-return-audit-063', 'commercial-return-audit-064'),
                          ('COMMERCIAL063', 'COMMERCIAL064'),
                          ('ordered_chain_equals_full_063', 'ordered_chain_equals_full_064'),
                          ('retain-commercial-entries-063.py', 'retain-commercial-entries-064.py'),
                          ('Original account lifecycle retry 063', 'Original boot event and ACL observation 064')]:
        source = source.replace(before, after)
    return source
