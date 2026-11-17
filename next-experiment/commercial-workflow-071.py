from pathlib import Path
import json
import runpy
import sys

b=Path(__file__).resolve().parent
previous=runpy.run_path(str(b/'commercial-workflow-070.py'))
configure_local_transport=previous['configure_local_transport']


def source071(name):
    if name=='install-commercial-native':
        test=json.loads((b.parent/'reports/commercial61-native-071/admission-test.json').read_text())
        assert all(test[k] for k in ['exact_observer_source_delta','all_other_archive_members_unchanged',
            'original_resource_files_unchanged','execute_only_register_observations','compiled_helpers_passed'])
    source=previous['source070'](name)
    for before,after in [('commercial61-native-070','commercial61-native-071'),
        ('commercial-return-audit-070','commercial-return-audit-071'),('COMMERCIAL070','COMMERCIAL071'),
        ('ordered_chain_equals_full_070','ordered_chain_equals_full_071'),
        ('retain-commercial-entries-070.py','retain-commercial-entries-071.py'),
        ('Original HAP rawfile layout 070','Original codec return registers 071')]:
        source=source.replace(before,after)
    return source


if __name__=='__main__':
    allowed=['install-commercial-native','run-commercial-native','retrieve-commercial-evidence','verify-commercial-return']
    assert len(sys.argv)==2 and sys.argv[1] in allowed
    configure_local_transport()
    exec(compile(source071(sys.argv[1]),__file__,'exec'),{'__name__':'__main__','__file__':__file__})
