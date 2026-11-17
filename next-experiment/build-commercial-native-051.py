from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-050.py'))
inner = p['inner']
outer = p['outer'].replace('commercial61-native-050', 'commercial61-native-051')
outer = runpy.run_path(str(b / 'commercial-hwbreak-051.py'))['replace_resolver'](outer)
outer = outer.replace('COMMERCIAL050', 'COMMERCIAL051')
payload = p['payload'].replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1)
payload = payload.replace('commercial61-native-050', 'commercial61-native-051')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
