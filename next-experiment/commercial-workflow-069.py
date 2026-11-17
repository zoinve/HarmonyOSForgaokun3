from pathlib import Path
import json
import runpy
import sys

b = Path(__file__).resolve().parent
previous = runpy.run_path(str(b / 'commercial-workflow-068.py'))
configure_local_transport = previous['configure_local_transport']


def source069(name):
    if name == 'install-commercial-native':
        test = json.loads((b.parent / 'reports/commercial61-native-069/admission-test.json').read_text())
        assert test['exact_delta_from_068'] == ['init','native-target/bootstrap']
        assert all(test[k] for k in ['compiled_observer_passed','fixture_source_unchanged',
            'exact_read_only_source_addition','all_other_archive_members_byte_identical',
            'original_service_credentials_unchanged'])
        assert not test['live_private_object_reads'] and not test['filesystem_mutation_by_observer']
    source = previous['source068'](name)
    for before, after in [
        ('commercial61-native-068', 'commercial61-native-069'),
        ('commercial-return-audit-068', 'commercial-return-audit-069'),
        ('COMMERCIAL068', 'COMMERCIAL069'),
        ('ordered_chain_equals_full_068', 'ordered_chain_equals_full_069'),
        ('retain-commercial-entries-068.py', 'retain-commercial-entries-069.py'),
        ('Completed full-resolution evidence 068', 'Original UI resource path inventory 069')]:
        source = source.replace(before, after)
    return source


if __name__ == '__main__':
    allowed = ['install-commercial-native','run-commercial-native',
               'retrieve-commercial-evidence','verify-commercial-return']
    assert len(sys.argv) == 2 and sys.argv[1] in allowed
    configure_local_transport()
    exec(compile(source069(sys.argv[1]),__file__,'exec'),
         {'__name__':'__main__','__file__':__file__})
