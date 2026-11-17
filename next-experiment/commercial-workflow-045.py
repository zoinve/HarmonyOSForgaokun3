"""Keep original protections and pin the independent authentic-PID target kernel."""
from pathlib import Path
import json
import runpy

base = Path(__file__).resolve().parents[1]
previous = runpy.run_path(str(Path(__file__).with_name('commercial-workflow-044.py')))
configure_local_transport = previous['configure_local_transport']


def source045(name):
    text = previous['source044'](name)
    for old, new in [('commercial61-native-044', 'commercial61-native-045'),
                     ('commercial-return-audit-044', 'commercial-return-audit-045'),
                     ('COMMERCIAL044', 'COMMERCIAL045'),
                     ('ordered_chain_equals_full_044', 'ordered_chain_equals_full_045'),
                     ('Original tokenless Binder delivery 044', 'Authentic oneway caller PID 045')]:
        text = text.replace(old, new)
    if name == 'install-commercial-native':
        kernel = json.loads((base / 'reports/native-binder-kernel-045/result.json').read_text())
        assert kernel['old_source_config_unchanged'] and kernel['original_tokens_uid_checks_unchanged']
        assert kernel['oneway_sender_pid_from_held_authentic_pid']
        text = text.replace("kernel=esp/'native-original-graphics-031/linux'", "kernel=esp/'native-original-graphics-045/linux'")
        text = text.replace("'linux /native-original-graphics-031/linux'", "'linux /native-original-graphics-045/linux'")
        text = text.replace('6fa44a5f1996a82bc95e8c44b3d32a69cc14d3789e39cffa2fcafafb7c294ff5', kernel['sha256'])
    return text
