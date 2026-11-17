"""Inherit the preserved single-boot workflow and admit the late observer delta."""
from pathlib import Path
import json
import runpy
import sys

b = Path(__file__).resolve().parent
previous = runpy.run_path(str(b / 'commercial-workflow-066.py'))
configure_local_transport = previous['configure_local_transport']


def source067(name):
    if name == 'install-commercial-native':
        test = json.loads((b.parent / 'reports/commercial61-native-067/admission-test.json').read_text())
        assert test['exact_delta_from_066'] == [
            'init', 'native-target/graphics016/system/lib64/libEGL_impl.so']
        assert all(test[k] for k in ['bootstrap_byte_identical',
            'all_other_members_byte_identical', 'diagnostic_gate_test_passed',
            'public_exports_unchanged'])
    source = previous['source066'](name)
    for before, after in [
        ('commercial61-native-066', 'commercial61-native-067'),
        ('commercial-return-audit-066', 'commercial-return-audit-067'),
        ('COMMERCIAL066', 'COMMERCIAL067'),
        ('ordered_chain_equals_full_066', 'ordered_chain_equals_full_067'),
        ('retain-commercial-entries-066.py', 'retain-commercial-entries-067.py'),
        ('Bounded complete presentation trace 066', 'Bounded late EGL observations 067')]:
        source = source.replace(before, after)
    return source


if __name__ == '__main__':
    allowed = ['install-commercial-native', 'run-commercial-native',
               'retrieve-commercial-evidence', 'verify-commercial-return']
    assert len(sys.argv) == 2 and sys.argv[1] in allowed
    configure_local_transport()
    exec(compile(source067(sys.argv[1]), __file__, 'exec'),
         {'__name__': '__main__', '__file__': __file__})
