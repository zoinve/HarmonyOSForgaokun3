"""Original account-service retry after SceneBoard, with bounded file evidence."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-062.py'))
helper = runpy.run_path(str(b / 'commercial-account-order-063.py'))
inner = p['inner']
outer = helper['instrument_outer'](p['outer'])
outer = outer.replace('commercial61-native-062', 'commercial61-native-063').replace('COMMERCIAL062', 'COMMERCIAL063')
payload = p['payload'].replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1)
payload = payload.replace('commercial61-native-062', 'commercial61-native-063')
assert payload.count("base/'commercial-desktop-order-062.py'") == 1
payload = payload.replace("base/'commercial-desktop-order-062.py'", "base/'commercial-account-order-063.py'", 1)
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
