"""Full historical-chain admission for a bounded BMS recovery observation."""
from pathlib import Path

BASE=Path(__file__).resolve().parent


def once(source,old,new):
    assert source.count(old)==1,old
    return source.replace(old,new,1)


if __name__=='__main__':
    source=(BASE/'test-commercial-admission-197.py').read_text()
    for old,new in [('commercial61-native-197-r1','commercial61-native-205'),
                    ('commercial61-native-197','commercial61-native-205'),
                    ('rebuild197-','rebuild205-'),
                    ('commercial-workflow-197.py','commercial-workflow-205.py'),
                    ("workflow['source197']", "workflow['source205']"),
                    ('estimated197','estimated205'),('settings197_preflight','settings205_preflight'),
                    ('set197.img','set205.img'),
                    ('eighteen_focused_test_scripts_pass','twenty_focused_test_scripts_pass'),
                    ('prior173_and175_runs_excluded','prior173_175_197_and201_runs_excluded')]:
        assert old in source,old
        source=source.replace(old,new)
    source=once(source,"parent=BUILD/'commercial61-native-173'","parent=BUILD/'commercial61-native-201'")
    start=source.index("    expected=(parent/'init.c').read_text()")
    end=source.index('    with tempfile.TemporaryDirectory(',start)
    replacement='''    adapt=runpy.run_path(str(BASE/'settings-native-205.py'))
    assert (work/'init.c').read_text()==adapt['outer205']((parent/'init.c').read_text())
    for name in ['persistent-data-166.h','persistent-data-172.h','persistent-unmount-plan-201.h']:
        assert (work/name).read_bytes()==(parent/name).read_bytes()
    assert (work/'settings-launch-205.h').read_text()==adapt['header205']()
    for name,digest in metadata['settings205']['header_hashes'].items():
        assert sha((work/name).read_bytes())==digest
'''
    source=source[:start]+replacement+source[end:]
    source=once(source,"    tests=['test-persistent-runtime-173.py'", "    tests=['test-settings-native-205.py','test-settings-native-201.py','test-persistent-runtime-173.py'")
    source=once(source,"    compile(workflow['PREFLIGHT'],'preflight197','exec')\n",'')
    source=once(source,"            assert 'attempt_count=1' in source and '660' in source and 'set205.img' in source",
        "            assert 'attempt_count=1' in source and '1260' in source and 'set205.img' in source\n            assert 'e7e18b21f4e1d0d6a4acd652edc13b64c0ab4f3540ea6ddb155ea107f4e57fb4' in source")
    anchor="                                ('commercial61-native-175-compile-fix-1','early-return-inspection.json')]:"
    source=once(source,anchor,"                                ('commercial61-native-175-compile-fix-1','early-return-inspection.json'),\n                                ('commercial61-native-197-r1','runtime-evidence/retrieval-manifest.json'),\n                                ('commercial61-native-201','runtime-evidence/retrieval-manifest.json')]:")
    exec(compile(source,'test-commercial-admission-205.generated.py','exec'),
        {'__name__':'__main__','__file__':str(BASE/'test-commercial-admission-205.generated.py')})
