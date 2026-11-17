from pathlib import Path
import json
import runpy

b = Path(__file__).resolve().parent
previous = runpy.run_path(str(b / 'commercial-workflow-061.py'))
configure_local_transport = previous['configure_local_transport']


def source062(name):
    if name == 'install-commercial-native':
        test = json.loads((b.parent / 'reports/commercial61-native-062/hwbreak-test-revision2.json').read_text())
        audit = json.loads((b.parent / 'reports/commercial-render-audit-061/result.json').read_text())
        assert test['processing_specifications'] == audit['probes']
        for key in ['synthetic_ring_tests_passed', 'executable_memory_tests_passed',
                    'modules_byte_identical_to_045', 'original_bootstrap_byte_identical',
                    'original_userland_binaries_byte_identical', 'eighth_register_x9_tested',
                    'public_parameter_and_account_order_only_change_tested', 'account_order_tests_passed']:
            assert test[key], key
        assert sorted(test['exact_delta_from_061']) == ['init', 'native-target/desktop-order020.sh']
    text = previous['source061'](name)
    for old, new in [('commercial61-native-061', 'commercial61-native-062'),
                     ('commercial-return-audit-061', 'commercial-return-audit-062'),
                     ('COMMERCIAL061', 'COMMERCIAL062'),
                     ('ordered_chain_equals_full_061', 'ordered_chain_equals_full_062'),
                     ('retain-commercial-entries-061.py', 'retain-commercial-entries-062.py')]:
        text = text.replace(old, new)
    return text
