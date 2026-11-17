"""Retain 066 lifecycle/capture behavior and use bounded late EGL observations."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-066.py'))
inner = p['inner']
outer = p['outer'].replace('commercial61-native-066', 'commercial61-native-067').replace(
    'COMMERCIAL066', 'COMMERCIAL067')
payload = p['payload'].replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1)
payload = payload.replace('commercial61-native-066', 'commercial61-native-067')
assert payload.count("root/'commercial-egl-035/result.json'") == 1
assert payload.count("root/'commercial-egl-035/libEGL_impl.so'") == 1
payload = payload.replace("root/'commercial-egl-035/", "root/'commercial-egl-067/")
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
