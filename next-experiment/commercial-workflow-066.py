from pathlib import Path
import json
import runpy

b = Path(__file__).resolve().parent
previous = runpy.run_path(str(b / 'commercial-workflow-065.py'))
configure_local_transport = previous['configure_local_transport']


def source066(name):
    if name == 'install-commercial-native':
        test = json.loads((b.parent / 'reports/commercial61-native-066/perf-stream-test.json').read_text())
        assert test['exact_delta_from_065'] == ['init', 'native-target/bootstrap']
        assert test['exact_read_only_source_delta'] and test['all_other_archive_members_byte_identical']
        assert test['synthetic_ring_tests_passed'] and test['bounded_stream_bytes'] == 262144
    source = previous['source065'](name)
    for before, after in [('commercial61-native-065', 'commercial61-native-066'),
                          ('commercial-return-audit-065', 'commercial-return-audit-066'),
                          ('COMMERCIAL065', 'COMMERCIAL066'),
                          ('ordered_chain_equals_full_065', 'ordered_chain_equals_full_066'),
                          ('retain-commercial-entries-065.py', 'retain-commercial-entries-066.py'),
                          ('Original chipset root alias restoration 065', 'Bounded complete presentation trace 066')]:
        source = source.replace(before, after)
    return source
