"""Reuse exact 086 observations, retaining inherited helper/diagnostic labels."""
from pathlib import Path
import runpy
import sys

BASE = Path(__file__).resolve().parent
SCRIPTS = {
    'artifacts': 'analyze-commercial-artifacts-086.py',
    'network': 'analyze-commercial-network-086.py',
    'native-network': 'analyze-commercial-native-netmanager-086.py',
    'probes': 'analyze-commercial-probes-086.py',
    'frame': 'analyze-commercial-full-frame-086.py',
    'second-frame': 'analyze-commercial-second-frame-086.py',
    'secrecy': 'audit-wifi-evidence-secrecy-086.py',
}


def source087(kind):
    path = BASE / SCRIPTS[kind]
    if kind == 'artifacts':
        source = path.read_text()
    else:
        source = runpy.run_path(str(path))['source']
    source = source.replace('commercial61-native-086', 'commercial61-native-087')
    if kind in ('frame', 'second-frame', 'network'):
        source = source.replace('COMMERCIAL086', 'COMMERCIAL087')
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in SCRIPTS
    exec(compile(source087(sys.argv[1]), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
