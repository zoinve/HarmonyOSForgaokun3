"""Keep full-frame 068 capture and observe original StartupGuide file paths."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-068.py'))
h = runpy.run_path(str(b / 'commercial-resource-inventory-069.py'))
inner = h['instrument'](p['inner'])
outer = p['outer'].replace('commercial61-native-068', 'commercial61-native-069').replace(
    'COMMERCIAL068', 'COMMERCIAL069')
payload = p['payload'].replace('inner=' + repr(p['inner']), 'inner=' + repr(inner), 1).replace(
    'outer=' + repr(p['outer']), 'outer=' + repr(outer), 1)
payload = payload.replace('commercial61-native-068', 'commercial61-native-069')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
