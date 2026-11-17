"""Observe original RS on kernel 045 with perf hardware execute breakpoints."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-045.py'))
inner = p['inner']
outer = p['outer'].replace('commercial61-native-045', 'commercial61-native-050').replace('COMMERCIAL045', 'COMMERCIAL050')
outer = runpy.run_path(str(b / 'commercial-hwbreak-050.py'))['instrument'](outer)
payload = p['payload'].replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1)
payload = payload.replace('commercial61-native-045', 'commercial61-native-050')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
