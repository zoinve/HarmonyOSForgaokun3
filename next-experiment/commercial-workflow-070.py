from pathlib import Path
import json
import runpy
import sys

b = Path(__file__).resolve().parent
previous = runpy.run_path(str(b / 'commercial-workflow-069.py'))
configure_local_transport = previous['configure_local_transport']


def source070(name):
    if name == 'install-commercial-native':
        test = json.loads((b.parent/'reports/commercial61-native-070/admission-test.json').read_text())
        assert all(test[k] for k in ['all_original_members_unchanged_except_init_bootstrap',
            'exact_original_rawfiles','readonly_overlay','no_installed_record_changes',
            'no_private_abi_hooks','extractor_negative_tests_passed'])
    source = previous['source069'](name)
    for before, after in [
        ('commercial61-native-069','commercial61-native-070'),
        ('commercial-return-audit-069','commercial-return-audit-070'),
        ('COMMERCIAL069','COMMERCIAL070'),
        ('ordered_chain_equals_full_069','ordered_chain_equals_full_070'),
        ('retain-commercial-entries-069.py','retain-commercial-entries-070.py'),
        ('Original UI resource path inventory 069','Original HAP rawfile layout 070')]:
        source = source.replace(before, after)
    return source


if __name__ == '__main__':
    allowed=['install-commercial-native','run-commercial-native','retrieve-commercial-evidence','verify-commercial-return']
    assert len(sys.argv)==2 and sys.argv[1] in allowed
    configure_local_transport()
    exec(compile(source070(sys.argv[1]),__file__,'exec'),{'__name__':'__main__','__file__':__file__})
