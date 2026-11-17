from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-052.py'))
inner = p['inner']
outer = runpy.run_path(str(b / 'commercial-hwbreak-054.py'))['instrument'](p['outer'])
outer = outer.replace('commercial61-native-052', 'commercial61-native-054').replace('COMMERCIAL052', 'COMMERCIAL054')
payload = p['payload'].replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1)
payload = payload.replace('commercial61-native-052', 'commercial61-native-054')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
