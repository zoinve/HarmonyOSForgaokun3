from pathlib import Path
import json
import runpy

b = Path(__file__).resolve().parent
previous = runpy.run_path(str(b / 'commercial-workflow-064.py'))
configure_local_transport = previous['configure_local_transport']


def source065(name):
    if name == 'install-commercial-native':
        test = json.loads((b.parent / 'reports/commercial61-native-065/hwbreak-test-revision3.json').read_text())
        audit = json.loads((b.parent / 'reports/commercial-root-layout-audit-065/result.json').read_text())
        assert audit['bootstrap_exact_addition_verified']
        assert test['bootstrap_only_original_layout_alias_added']
        assert test['public_parameter_account_and_root_layout_delta_tested']
        assert not test['original_bootstrap_byte_identical']
        assert test['exact_delta_from_064'] == ['init', 'native-target/bootstrap']
        for key in ['public_event_diagnostics_tested', 'synthetic_ring_tests_passed',
                    'executable_memory_tests_passed', 'modules_byte_identical_to_045',
                    'original_userland_binaries_byte_identical', 'account_order_tests_passed']:
            assert test[key], key
    source = previous['source064'](name)
    for before, after in [('commercial61-native-064', 'commercial61-native-065'),
                          ('commercial-return-audit-064', 'commercial-return-audit-065'),
                          ('COMMERCIAL064', 'COMMERCIAL065'),
                          ('ordered_chain_equals_full_064', 'ordered_chain_equals_full_065'),
                          ('retain-commercial-entries-064.py', 'retain-commercial-entries-065.py'),
                          ('Original boot event and ACL observation 064', 'Original chipset root alias restoration 065')]:
        source = source.replace(before, after)
    return source
