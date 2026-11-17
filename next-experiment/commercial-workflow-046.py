"""Preserve original workflow protections and pin the independent trace kernel."""
from pathlib import Path
import json
import runpy

b = Path(__file__).resolve().parent
previous = runpy.run_path(str(b / 'commercial-workflow-045.py'))
configure_local_transport = previous['configure_local_transport']


def source046(name):
    text = previous['source045'](name)
    for old, new in [('commercial61-native-045', 'commercial61-native-046'),
                     ('commercial-return-audit-045', 'commercial-return-audit-046'),
                     ('COMMERCIAL045', 'COMMERCIAL046'),
                     ('ordered_chain_equals_full_045', 'ordered_chain_equals_full_046'),
                     ('Authentic oneway caller PID 045', 'Original service execution trace 046')]:
        text = text.replace(old, new)
    if name == 'install-commercial-native':
        old = json.loads((b.parent / 'reports/native-binder-kernel-045/result.json').read_text())
        new = json.loads((b.parent / 'reports/native-trace-kernel-046/result.json').read_text())
        assert new['source_unchanged'] and new['old_source_config_unchanged']
        assert new['security_config_unchanged'] and new['target_only_trace_capability']
        text = text.replace('native-original-graphics-045/linux', 'native-original-graphics-046/linux')
        text = text.replace(old['sha256'], new['sha256'])
    return text
