"""Keep 067 services/rendering and add completed full-resolution evidence."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-067.py'))
h = runpy.run_path(str(b / 'commercial-full-export-068.py'))
inner = h['inner'](p['inner'])
outer = h['outer'](p['outer']).replace('commercial61-native-067', 'commercial61-native-068').replace(
    'COMMERCIAL067', 'COMMERCIAL068')
payload = p['payload'].replace('inner=' + repr(p['inner']), 'inner=' + repr(inner), 1).replace(
    'outer=' + repr(p['outer']), 'outer=' + repr(outer), 1)
payload = payload.replace('commercial61-native-067', 'commercial61-native-068')
assert payload.count("root/'commercial-composer-030/result.json'") == 1
assert payload.count("root/'commercial-composer-030/libdisplay_composer_vdi_impl.z.so'") == 1
payload = payload.replace("root/'commercial-composer-030/", "root/'commercial-composer-068/")
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
