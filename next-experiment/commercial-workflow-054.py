from pathlib import Path
import json
import runpy

b = Path(__file__).resolve().parent
previous = runpy.run_path(str(b / 'commercial-workflow-050.py'))
configure_local_transport = previous['configure_local_transport']


def source054(name):
    if name == 'install-commercial-native':
        test = json.loads((b.parent / 'reports/commercial61-native-054/hwbreak-test.json').read_text())
        for key in ['synthetic_ring_tests_passed', 'executable_memory_tests_passed', 'processing_specs_audited',
                    'modules_byte_identical_to_045', 'original_bootstrap_byte_identical',
                    'original_userland_byte_identical']:
            assert test[key], key
    text = previous['source050'](name)
    for old, new in [('commercial61-native-050', 'commercial61-native-054'),
                     ('commercial-return-audit-050', 'commercial-return-audit-054'),
                     ('COMMERCIAL050', 'COMMERCIAL054'),
                     ('ordered_chain_equals_full_050', 'ordered_chain_equals_full_054'),
                     ('Original RS hardware observation 050', 'Original RS mapped-file observation 054')]:
        text = text.replace(old, new)
    return text
