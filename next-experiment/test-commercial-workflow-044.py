"""Verify that only the declared observer changes differ from the completed 043."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
old = runpy.run_path(str(b / 'build-commercial-native-043.py'))
new = runpy.run_path(str(b / 'build-commercial-native-044.py'))
outer = old['outer'].replace('commercial61-native-043', 'commercial61-native-044').replace('COMMERCIAL043', 'COMMERCIAL044')
assert new['outer'] == runpy.run_path(str(b / 'commercial-outer-binder-044.py'))['instrument'](outer)
assert new['inner'] == old['inner'].replace('libcommercial_rs_observer043.so', 'libcommercial_rs_observer044.so')
for token in ['target_budget_seconds=150', 'elapsed033<150', 'left033=270', 'CLONE_NEWPID|CLONE_NEWNS|CLONE_NEWNET|SIGCHLD']:
    assert token in new['outer'], token
assert 'strcmp(expected,actual)' in new['outer']
assert 'commercial_outer_stream044(path,262144)' in new['outer']
assert 'COMMERCIAL043_STREAM_END' in new['inner']
for name in ['install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence',
             'verify-commercial-return', 'analyze-commercial-minimal']:
    source = runpy.run_path(str(b / (name + '-044.py')))['source']
    compile(source, name, 'exec')
    assert 'commercial61-native-044' in source and 'commercial61-native-043' not in source
    if name != 'analyze-commercial-minimal':
        for token in ['StrictHostKeyChecking=yes', 'HostName=192.168.10.128', 'HostKeyAlias=192.168.10.128']:
            assert token in source, (name, token)
verify = runpy.run_path(str(b / 'verify-commercial-return-044.py'))['source']
for token in ["=='enabled'", "=='active'", 'removed_entries', 'commercial_original_images_unchanged']:
    assert token in verify
print('PASS: original desktop launch, inner runtime and 150/270 guards; declared outer observation only; strict SSH and preservation')
