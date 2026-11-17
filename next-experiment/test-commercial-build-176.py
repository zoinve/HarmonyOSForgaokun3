"""Verify the complete candidate build; do not claim deployment admission."""
from pathlib import Path

BASE = Path(__file__).resolve().parent

if __name__ == '__main__':
    source = (BASE / 'test-commercial-admission-166.py').read_text()
    source = source[:source.index("    workflow=runpy.run_path(")]
    for old, new in [
        ('commercial61-native-166-compile-fix-1', 'commercial61-native-176'),
        ('commercial61-native-166', 'commercial61-native-176'),
        ('admission-test.json', 'build-test.json'),
        ('build-commercial-native-166.py', 'build-commercial-native-176.py'),
        ("generator['runtime166']", "generator['runtime176']"),
        ("generator['outer166']", "generator['outer176']"),
        ("['persistent-data-166.h','persistent-runtime-166.h']", "['persistent-data-172.h','persistent-runtime-173.h']"),
        ("tests=['test-persistent-data-166.py',", "tests=['test-usb-readonly-176.py','test-usb-readonly-175.py','test-native-usb-storage-174.py','test-persistent-runtime-173.py','test-persistent-lifecycle-172.py','test-persistent-runtime-168.py','test-persistent-data-166.py',"),
    ]:
        assert old in source, old
        source = source.replace(old, new)
    source += '''
    baseline=BUILD/'commercial61-native-173'
    for name in ['bootstrap-runtime087','bootstrap-runtime087.c']:
        assert (work/name).read_bytes()==(baseline/name).read_bytes()
    for key,name in [('observer_sha256','native-usb-storage-174.h'),
                     ('guard_sha256','usb-readonly-175.h'),('trace_sha256','usb-readonly-176.h')]:
        assert sha((BASE/name).read_bytes())==metadata['usb176'][key]
    init=(work/'init.c').read_text()
    assert init.count('#include "usb-readonly-176.h"')==1
    assert init.count('if (native_usb_storage175_guard())return;')==1
    assert init.index('if (native_usb_storage175_guard())return;')<init.index('if(okay && persistent166_prepare())')
    result=dict(complete_29_archive_chain_equals_full=True,reproducible_arm64_build=True,
        focused_test_script_count=len(tests),desktop173_runtime_byte_identical=True,
        trace_and_guard_hashes_verified=True,installed=False,booted=False,
        deployment_workflow_verified=False,native_usb_acceptance=False)
    (report/'build-test.json').open('x').write(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
'''
    exec(compile(source, 'test-commercial-build-176.generated.py', 'exec'),
         {'__name__': '__main__', '__file__': str(BASE / 'test-commercial-build-176.generated.py')})
