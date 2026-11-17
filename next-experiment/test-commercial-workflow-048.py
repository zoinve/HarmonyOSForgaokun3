from pathlib import Path
import json
import runpy

b = Path(__file__).resolve().parent
w = runpy.run_path(str(b / 'commercial-workflow-048.py'))
p = runpy.run_path(str(b / 'build-commercial-native-048.py'))
assert p['inner'] == runpy.run_path(str(b / 'build-commercial-native-047.py'))['inner']
for name in ['install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence', 'verify-commercial-return', 'analyze-commercial-minimal']:
    source = w['source048'](name)
    compile(source, name, 'exec')
    assert 'commercial61-native-048' in source and 'commercial61-native-047' not in source
    if name != 'analyze-commercial-minimal':
        for token in ['StrictHostKeyChecking=yes', 'HostName=192.168.10.128', 'HostKeyAlias=192.168.10.128']:
            assert token in source
install = w['source048']('install-commercial-native')
kernel = json.loads((b.parent / 'reports/native-trace-kernel-047/result.json').read_text())
assert kernel['image_sha256'] in install
assert "kernel=esp/'native-original-graphics-047/linux'" in install
for token in ['COMMERCIAL048_TRACE_CONTROL_BEGIN', 'COMMERCIAL048_TRACE_CONTROL_END', 'commercial048/', 'events/commercial048', 'unsigned left033=270']:
    assert token in p['outer']
assert 'COMMERCIAL047_TRACE' not in p['outer']
verify = w['source048']('verify-commercial-return')
for token in ["=='enabled'", "=='active'", 'removed_entries', 'commercial_original_images_unchanged']:
    assert token in verify
print('PASS: unchanged target bootstrap; matching 047 kernel/modules; persisted 048 trace control boundaries and boot protections')
