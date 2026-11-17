"""Preserved one-shot workflow with admission for completed real-image capture."""
from pathlib import Path
import json
import runpy
import sys

b = Path(__file__).resolve().parent
previous = runpy.run_path(str(b / 'commercial-workflow-067.py'))
configure_local_transport = previous['configure_local_transport']


def source068(name):
    if name == 'install-commercial-native':
        test = json.loads((b.parent / 'reports/commercial61-native-068/admission-test.json').read_text())
        assert test['exact_delta_from_067'] == ['init', 'native-target/bootstrap',
            'native-target/graphics016/vendor/lib64/libdisplay_composer_vdi_impl.z.so']
        assert all(test[k] for k in ['all_other_members_byte_identical',
            'original_service_and_egl_members_byte_identical', 'full_capture_helpers_tested',
            'diagnostic_source_additions_only', 'original_service_credentials_unchanged'])
    source = previous['source067'](name)
    for before, after in [
        ('commercial61-native-067', 'commercial61-native-068'),
        ('commercial-return-audit-067', 'commercial-return-audit-068'),
        ('COMMERCIAL067', 'COMMERCIAL068'),
        ('ordered_chain_equals_full_067', 'ordered_chain_equals_full_068'),
        ('retain-commercial-entries-067.py', 'retain-commercial-entries-068.py'),
        ('Bounded late EGL observations 067', 'Completed full-resolution evidence 068')]:
        source = source.replace(before, after)
    return source


if __name__ == '__main__':
    allowed = ['install-commercial-native', 'run-commercial-native',
               'retrieve-commercial-evidence', 'verify-commercial-return']
    assert len(sys.argv) == 2 and sys.argv[1] in allowed
    configure_local_transport()
    exec(compile(source068(sys.argv[1]), __file__, 'exec'),
         {'__name__': '__main__', '__file__': __file__})
