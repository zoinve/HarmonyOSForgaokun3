from pathlib import Path
import json
import runpy

b = Path(__file__).resolve().parent
previous = runpy.run_path(str(b / 'commercial-workflow-045.py'))
configure_local_transport = previous['configure_local_transport']


def source050(name):
    if name == 'install-commercial-native':
        test = json.loads((b.parent / 'reports/commercial61-native-050/hwbreak-test.json').read_text())
        assert test['synthetic_ring_tests_passed'] and test['modules_byte_identical_to_045']
        assert test['original_bootstrap_byte_identical'] and test['original_userland_byte_identical']
    text = previous['source045'](name)
    for old, new in [('commercial61-native-045', 'commercial61-native-050'),
                     ('commercial-return-audit-045', 'commercial-return-audit-050'),
                     ('COMMERCIAL045', 'COMMERCIAL050'),
                     ('ordered_chain_equals_full_045', 'ordered_chain_equals_full_050'),
                     ('Authentic oneway caller PID 045', 'Original RS hardware observation 050')]:
        text = text.replace(old, new)
    return text
