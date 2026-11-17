"""Unchanged native userland; observe original RS execution with target uprobes."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-045.py'))
inner = p['inner']
outer = p['outer'].replace('commercial61-native-045', 'commercial61-native-046').replace('COMMERCIAL045', 'COMMERCIAL046')
outer = runpy.run_path(str(b / 'commercial-trace-046.py'))['instrument'](outer)
payload = p['payload'].replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1)
payload = payload.replace('commercial61-native-045', 'commercial61-native-046')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
