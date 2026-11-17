"""Correct the rejected 076 init argv without changing original services."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-076.py'))
inner = p['inner']
outer = p['outer'].replace('commercial61-native-076', 'commercial61-native-077').replace('COMMERCIAL076', 'COMMERCIAL077')
payload = p['payload'].replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1)
payload = payload.replace('commercial61-native-076', 'commercial61-native-077').replace(
    'commercial-init-desktop-076.py', 'commercial-init-desktop-077.py')
anchor = 'record076=dict('
assert payload.count(anchor) == 1
payload = payload.replace(anchor,
    "entries['native-target/commercial-desktop077.sh']=(stat.S_IFREG|0o755,module076['SCRIPT'].encode())\n" + anchor, 1)
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
