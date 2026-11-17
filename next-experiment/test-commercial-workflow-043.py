"""Static launch and preservation checks; no completed operational run is repeated."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
old = runpy.run_path(str(b / 'build-commercial-native-042.py'))
new = runpy.run_path(str(b / 'build-commercial-native-043.py'))
assert new['outer'] == old['outer'].replace('commercial61-native-042', 'commercial61-native-043').replace('COMMERCIAL042', 'COMMERCIAL043')
for token in ['target_budget_seconds=150', 'elapsed033<150', 'left033=270']:
    assert token in new['outer'], token
assert 'COMMERCIAL043_STREAM_END' in new['inner'] and 'eof=%d' in new['inner']
assert 'commercial_stream043(path,sample,pid,1048576)' in new['inner']
assert 'char maps[32768]' not in new['inner']
assert 'libcommercial_rs_observer043.so' in new['inner']
assert 'libcommercial_rs_observer042.so' not in new['inner']
for name in ['install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence',
             'verify-commercial-return', 'analyze-commercial-minimal']:
    source = runpy.run_path(str(b / (name + '-043.py')))['source']
    compile(source, name, 'exec')
    assert 'commercial61-native-043' in source and 'commercial61-native-042' not in source
    if name != 'analyze-commercial-minimal':
        for token in ['StrictHostKeyChecking=yes', 'HostName=192.168.10.128', 'HostKeyAlias=192.168.10.128']:
            assert token in source, (name, token)
verify = runpy.run_path(str(b / 'verify-commercial-return-043.py'))['source']
for token in ["=='enabled'", "=='active'", 'removed_entries', 'commercial_original_images_unchanged']:
    assert token in verify
print('PASS: original outer runtime and launch retained; 150/270 guards, full maps, strict trusted SSH and archived removals')
