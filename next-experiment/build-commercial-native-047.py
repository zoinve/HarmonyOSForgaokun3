"""Original service tracing with a matching kernel-module set."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-046.py'))
inner = p['inner']
outer = p['outer'].replace('commercial61-native-046', 'commercial61-native-047').replace('COMMERCIAL046', 'COMMERCIAL047').replace('commercial046/', 'commercial047/').replace('events/commercial046', 'events/commercial047')
payload = p['payload'].replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1)
payload = payload.replace('commercial61-native-046', 'commercial61-native-047')
anchor = "raw=b''.join(member(n,m,d,i+1) for i,(n,(m,d)) in enumerate(entries.items()))"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, "import runpy\nrunpy.run_path(str(base/'commercial-modules-047.py'))['replace_modules'](entries,work,local)\n" + anchor, 1)
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
