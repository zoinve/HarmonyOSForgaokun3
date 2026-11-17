"""Restore only the original chipset-to-vendor alias in the diagnostic root."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-064.py'))
layout = runpy.run_path(str(b / 'commercial-root-layout-065.py'))
inner = layout['repair'](p['inner'])
outer = p['outer'].replace('commercial61-native-064', 'commercial61-native-065').replace('COMMERCIAL064', 'COMMERCIAL065')
payload = p['payload'].replace('inner=' + repr(p['inner']), 'inner=' + repr(inner), 1)
payload = payload.replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1)
payload = payload.replace('commercial61-native-064', 'commercial61-native-065')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
