from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-060.py'))
inner = p['inner']
outer = runpy.run_path(str(b / 'commercial-hwbreak-061.py'))['instrument'](p['outer'])
outer = outer.replace('commercial61-native-060', 'commercial61-native-061').replace('COMMERCIAL060', 'COMMERCIAL061')
payload = p['payload'].replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1)
payload = payload.replace('commercial61-native-060', 'commercial61-native-061')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
