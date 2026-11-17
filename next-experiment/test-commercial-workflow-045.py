"""Constrain the candidate to the authentic-PID kernel and new evidence labels."""
from pathlib import Path
import json
import runpy

b = Path(__file__).resolve().parent
old = runpy.run_path(str(b / 'build-commercial-native-044.py'))
new = runpy.run_path(str(b / 'build-commercial-native-045.py'))
assert old['inner'] == new['inner']
assert new['outer'] == old['outer'].replace('commercial61-native-044', 'commercial61-native-045').replace('COMMERCIAL044', 'COMMERCIAL045')
for token in ['elapsed033<150', 'left033=270', 'target_budget_seconds=150']:
    assert token in new['outer']
for name in ['install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence',
             'verify-commercial-return', 'analyze-commercial-minimal']:
    text = runpy.run_path(str(b / (name + '-045.py')))['source']
    compile(text, name, 'exec')
    assert 'commercial61-native-045' in text and 'commercial61-native-044' not in text
    if name != 'analyze-commercial-minimal':
        for token in ['StrictHostKeyChecking=yes', 'HostName=192.168.10.128', 'HostKeyAlias=192.168.10.128']:
            assert token in text
install = runpy.run_path(str(b / 'install-commercial-native-045.py'))['source']
kernel = json.loads((b.parent / 'reports/native-binder-kernel-045/result.json').read_text())
assert "kernel=esp/'native-original-graphics-045/linux'" in install
assert "'linux /native-original-graphics-045/linux'" in install
assert kernel['sha256'] in install
assert "dtb=esp/'native-original-graphics-031/sc8280xp-huawei-gaokun3.dtb'" in install
verify = runpy.run_path(str(b / 'verify-commercial-return-045.py'))['source']
for token in ["=='enabled'", "=='active'", 'removed_entries', 'commercial_original_images_unchanged']:
    assert token in verify
print('PASS: unchanged original userland and bounds; exact new diagnostic kernel pin; original DTB, SSH and preservation retained')
