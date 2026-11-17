from pathlib import Path
import json
import runpy

b = Path(__file__).resolve().parent
w = runpy.run_path(str(b / 'commercial-workflow-046.py'))
for name in ['install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence',
             'verify-commercial-return', 'analyze-commercial-minimal']:
    text = w['source046'](name)
    compile(text, name, 'exec')
    assert 'commercial61-native-046' in text and 'commercial61-native-045' not in text
    if name != 'analyze-commercial-minimal':
        for token in ['StrictHostKeyChecking=yes', 'HostName=192.168.10.128', 'HostKeyAlias=192.168.10.128']:
            assert token in text
install = w['source046']('install-commercial-native')
kernel = json.loads((b.parent / 'reports/native-trace-kernel-046/result.json').read_text())
assert kernel['sha256'] in install
assert "kernel=esp/'native-original-graphics-046/linux'" in install
assert "dtb=esp/'native-original-graphics-031/sc8280xp-huawei-gaokun3.dtb'" in install
verify = w['source046']('verify-commercial-return')
for token in ["=='enabled'", "=='active'", 'removed_entries', 'commercial_original_images_unchanged']:
    assert token in verify
print('PASS: exact 046 kernel; original DTB, SSH, image/default/timer/retention protections retained')
