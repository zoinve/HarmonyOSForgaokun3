"""Retain original wlan helper; enter target namespaces before P2P setup."""
from pathlib import Path
import runpy

BASE = Path(__file__).resolve().parent
SOURCE = runpy.run_path(str(BASE / 'commercial-network-helper-086.py'))['SOURCE']


def once(source, old, new):
    assert source.count(old) == 1, old
    return source.replace(old, new, 1)


SOURCE = once(SOURCE, '"freeze", "events"', '"freeze", "events", "share-start", "share-observe"')
SOURCE = once(SOURCE, '-c/network084/wpa.conf', '-c/share501/wlan.conf')
anchor = 'static int run_mode(const char *mode)\n{'
helper = (BASE / 'native-share-control-501.c').read_text()
SOURCE = once(SOURCE, anchor, helper + '\n' + anchor + '''
    if (!strcmp(mode,"share-start")) return share501_start();
    if (!strcmp(mode,"share-observe")) return share501_ping();''')
SOURCE = once(SOURCE, '        execv(start[0], start);',
    '        int config501 = share501_wlan();\n'
    '        if (config501) return config501;\n'
    '        execv(start[0], start);')
