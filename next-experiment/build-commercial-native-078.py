from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-077.py'))
inner = p['inner']
outer = p['outer'].replace('commercial61-native-077', 'commercial61-native-078').replace('COMMERCIAL077', 'COMMERCIAL078')
payload = p['payload'].replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1).replace(
    'commercial61-native-077', 'commercial61-native-078').replace(
    'commercial-init-desktop-077.py', 'commercial-init-desktop-078.py')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
