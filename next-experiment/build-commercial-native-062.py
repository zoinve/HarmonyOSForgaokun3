"""Keep 061 graphics/observation; retry original account activation after WMS."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-061.py'))
inner = p['inner']
outer = p['outer'].replace('commercial61-native-061', 'commercial61-native-062').replace('COMMERCIAL061', 'COMMERCIAL062')
payload = p['payload'].replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1)
payload = payload.replace('commercial61-native-061', 'commercial61-native-062')
before = "patched=runpy.run_path(str(base/'commercial-desktop-order-021.py'))['repair'](original)\npatched=runpy.run_path(str(base/'commercial-desktop-retry-032.py'))['repair'](patched)"
assert payload.count(before) == 1
payload = payload.replace(before, "patched=runpy.run_path(str(base/'commercial-desktop-order-062.py'))['repair'](original)", 1)
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
