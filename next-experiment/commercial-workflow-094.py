"""Distinct corrected candidate; 093 was installed but never booted."""
from pathlib import Path
import json
import runpy
import sys

BASE = Path(__file__).resolve().parent
previous = runpy.run_path(str(BASE/'commercial-workflow-093.py'))
configure_local_transport = previous['configure_local_transport']


def source094(name):
    if name == 'install-commercial-native':
        assert all(json.loads((BASE.parent/'reports/commercial61-native-094/admission-test.json').read_text()).values())
    source = previous['source093'](name).replace('commercial61-native-093', 'commercial61-native-094').replace(
        'commercial-return-audit-093', 'commercial-return-audit-094').replace(
        'ordered_chain_equals_full_093', 'ordered_chain_equals_full_094').replace(
        'retain-commercial-entries-093.py', 'retain-commercial-entries-094.py').replace(
        'early093.img', 'early094.img').replace('Original init physical hardware inputs 093',
        'Original init physical hardware inputs 094')
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ('install-commercial-native', 'run-commercial-native',
                                               'retrieve-commercial-evidence', 'verify-commercial-return')
    configure_local_transport()
    exec(compile(source094(sys.argv[1]), __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
