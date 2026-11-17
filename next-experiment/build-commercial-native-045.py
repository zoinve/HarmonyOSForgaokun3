"""Unchanged 044 userland, new numbered evidence for the authentic PID kernel fix."""
from pathlib import Path
import runpy

p = runpy.run_path(str(Path(__file__).with_name('build-commercial-native-044.py')))
inner = p['inner']
outer = p['outer'].replace('commercial61-native-044', 'commercial61-native-045').replace('COMMERCIAL044', 'COMMERCIAL045')
payload = p['payload'].replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1)
payload = payload.replace('commercial61-native-044', 'commercial61-native-045')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
