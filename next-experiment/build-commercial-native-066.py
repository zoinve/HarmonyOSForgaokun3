"""Keep 065 lifecycle fixes; capture the full bounded presentation trace."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-065.py'))
helper = runpy.run_path(str(b / 'commercial-perf-stream-066.py'))
inner = helper['repair'](p['inner'])
outer = p['outer'].replace('commercial61-native-065', 'commercial61-native-066').replace('COMMERCIAL065', 'COMMERCIAL066')
payload = p['payload'].replace('inner=' + repr(p['inner']), 'inner=' + repr(inner), 1)
payload = payload.replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1)
payload = payload.replace('commercial61-native-065', 'commercial61-native-066')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
