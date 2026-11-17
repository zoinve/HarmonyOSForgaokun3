from pathlib import Path
import json
import runpy

b = Path(__file__).resolve().parent
w = runpy.run_path(str(b / 'commercial-workflow-047.py'))
builder = runpy.run_path(str(b / 'build-commercial-native-047.py'))
assert builder['inner'] == runpy.run_path(str(b / 'build-commercial-native-046.py'))['inner']
for name in ['install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence',
             'verify-commercial-return', 'analyze-commercial-minimal']:
    text = w['source047'](name)
    compile(text, name, 'exec')
    assert 'commercial61-native-047' in text and 'commercial61-native-046' not in text
    if name != 'analyze-commercial-minimal':
        for token in ['StrictHostKeyChecking=yes', 'HostName=192.168.10.128', 'HostKeyAlias=192.168.10.128']:
            assert token in text
install = w['source047']('install-commercial-native')
kernel = json.loads((b.parent / 'reports/native-trace-kernel-047/result.json').read_text())
assert kernel['image_sha256'] in install
assert "kernel=esp/'native-original-graphics-047/linux'" in install
assert "dtb=esp/'native-original-graphics-031/sc8280xp-huawei-gaokun3.dtb'" in install
verify = w['source047']('verify-commercial-return')
for token in ["=='enabled'", "=='active'", 'removed_entries', 'commercial_original_images_unchanged']:
    assert token in verify
outer = builder['outer']
for token in ['COMMERCIAL047_TRACE_READY', 'commercial047/', 'events/commercial047', 'unsigned left033=270', 'target_timeout=1']:
    assert token in outer, token
assert 'COMMERCIAL046_TRACE' not in outer and 'events/commercial046' not in outer
print('PASS: unchanged original bootstrap; exact 047 kernel, matching modules, trace group, SSH and boot protections')
