from pathlib import Path
import json
import runpy

b = Path(__file__).resolve().parent
w = runpy.run_path(str(b / 'commercial-workflow-049.py'))
p = runpy.run_path(str(b / 'build-commercial-native-049.py'))
assert p['inner'] == runpy.run_path(str(b / 'build-commercial-native-048.py'))['inner']
for name in ['install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence', 'verify-commercial-return', 'analyze-commercial-minimal']:
    source = w['source049'](name)
    compile(source, name, 'exec')
    assert 'commercial61-native-049' in source and 'commercial61-native-048' not in source
    if name != 'analyze-commercial-minimal':
        for token in ['StrictHostKeyChecking=yes', 'HostName=192.168.10.128', 'HostKeyAlias=192.168.10.128']:
            assert token in source
install = w['source049']('install-commercial-native')
kernel = json.loads((b.parent / 'reports/native-trace-kernel-047/result.json').read_text())
assert kernel['image_sha256'] in install
assert "kernel=esp/'native-original-graphics-047/linux'" in install
for token in ['COMMERCIAL049_TRACE_STAGE', 'setup_begin', 'namespace_read_begin', 'process_scan_begin', 'instruction_open_begin', 'instruction_read_end', 'tracefs_mount_begin', 'tracefs_mount_end', 'existing_events_read_begin', 'diagnostics_begin', 'COMMERCIAL049_TRACE_CONTROL_BEGIN', 'unsigned left033=270']:
    assert token in p['outer'], token
assert 'COMMERCIAL048_TRACE' not in p['outer']
verify = w['source049']('verify-commercial-return')
for token in ["=='enabled'", "=='active'", 'removed_entries', 'commercial_original_images_unchanged']:
    assert token in verify
print('PASS: original bootstrap unchanged; exact matching kernel/modules; staged original-service setup and boot protections')
