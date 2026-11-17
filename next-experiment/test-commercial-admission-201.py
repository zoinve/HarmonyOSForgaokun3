'''Reuse complete-chain admission with exact201 source and fixed-launch checks.'''
from pathlib import Path

BASE=Path(__file__).resolve().parent


def once(source,old,new):
    assert source.count(old)==1,old
    return source.replace(old,new,1)


if __name__=='__main__':
    source=(BASE/'test-commercial-admission-197.py').read_text()
    for old,new in [('commercial61-native-197-r1','commercial61-native-201'),
                    ('commercial61-native-197','commercial61-native-201'),
                    ('rebuild197-','rebuild201-'),
                    ('commercial-workflow-197.py','commercial-workflow-201.py'),
                    ("workflow['source197']", "workflow['source201']"),
                    ('estimated197','estimated201'),('settings197_preflight','settings201_preflight'),
                    ('set197.img','set201.img'),
                    ('eighteen_focused_test_scripts_pass','nineteen_focused_test_scripts_pass'),
                    ('prior173_and175_runs_excluded','prior173_175_and197_runs_excluded')]:
        assert old in source,old
        source=source.replace(old,new)
    source=once(source,"parent=BUILD/'commercial61-native-173'","parent=BUILD/'commercial61-native-197-r1'")
    start=source.index("    expected=(parent/'init.c').read_text()")
    end=source.index('    with tempfile.TemporaryDirectory(',start)
    replacement='''    adapt=runpy.run_path(str(BASE/'settings-native-201.py'))
    assert (work/'init.c').read_text()==adapt['outer201']((parent/'init.c').read_text())
    assert (work/'persistent-data-166.h').read_bytes()==(parent/'persistent-data-166.h').read_bytes()
    assert (work/'persistent-data-172.h').read_text()==adapt['lifecycle201']((BASE/'persistent-data-172.h').read_text())
    assert (work/'persistent-unmount-plan-201.h').read_text()==adapt['plan201']((BASE/'persistent-unmount-plan-172.h').read_text())
    assert (work/'settings-launch-201.h').read_bytes()==(BASE/'settings-launch-201.h').read_bytes()
    for name,digest in metadata['settings201']['header_hashes'].items():
        assert sha((work/name).read_bytes())==digest
'''
    source=source[:start]+replacement+source[end:]
    source=once(source,"    tests=['test-persistent-runtime-173.py'", "    tests=['test-settings-native-201.py','test-persistent-runtime-173.py'")
    source=once(source,"    compile(workflow['PREFLIGHT'],'preflight197','exec')\n",'')
    source=once(source,"            assert 'attempt_count=1' in source and '660' in source and 'set201.img' in source",
        "            assert 'attempt_count=1' in source and '660' in source and 'set201.img' in source\n            assert '41fae8e1ceacedd356da6e6d712aa8a995179c042221657f4d8e2deace9938c6' in source")
    anchor="                                ('commercial61-native-175-compile-fix-1','early-return-inspection.json')]:"
    source=once(source,anchor,"                                ('commercial61-native-175-compile-fix-1','early-return-inspection.json'),\n                                ('commercial61-native-197-r1','runtime-evidence/retrieval-manifest.json')]:")
    exec(compile(source,'test-commercial-admission-201.generated.py','exec'),
        {'__name__':'__main__','__file__':str(BASE/'test-commercial-admission-201.generated.py')})
