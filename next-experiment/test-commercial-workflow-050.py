from pathlib import Path
import json
import runpy

b = Path(__file__).resolve().parent
w = runpy.run_path(str(b / 'commercial-workflow-050.py'))
for name in ['install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence', 'verify-commercial-return', 'analyze-commercial-minimal']:
    source = w['source050'](name)
    compile(source, name, 'exec')
    assert 'commercial61-native-050' in source and 'commercial61-native-045' not in source
    if name != 'analyze-commercial-minimal':
        for value in ['StrictHostKeyChecking=yes', 'HostName=192.168.10.128', 'HostKeyAlias=192.168.10.128']:
            assert value in source
install = w['source050']('install-commercial-native')
kernel = json.loads((b.parent / 'reports/native-binder-kernel-045/result.json').read_text())
assert kernel['sha256'] in install and "kernel=esp/'native-original-graphics-045/linux'" in install
assert "dtb=esp/'native-original-graphics-031/sc8280xp-huawei-gaokun3.dtb'" in install
verify = w['source050']('verify-commercial-return')
for value in ["=='enabled'", "=='active'", 'removed_entries', 'commercial_original_images_unchanged']:
    assert value in verify
p = runpy.run_path(str(b / 'build-commercial-native-050.py'))
assert p['inner'] == runpy.run_path(str(b / 'build-commercial-native-045.py'))['inner']
for value in ['hw050_tick(child,0)', 'hw050_tick(child,1)', 'unsigned left033=270', 'COMMERCIAL050 target_timeout=1']:
    assert value in p['outer']
print('PASS: exact 045 kernel/module route, unchanged original bootstrap, bounded observation and boot/image/timer safeguards')
