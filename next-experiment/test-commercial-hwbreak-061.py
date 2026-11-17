from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = runpy.run_path(str(b / 'test-commercial-hwbreak-060.py'))['source']
old_specs = runpy.run_path(str(b / 'commercial-hwbreak-060.py'))['specifications']()
new_specs = runpy.run_path(str(b / 'commercial-hwbreak-061.py'))['specifications']()
assert source.count(repr(old_specs)) == 1
source = source.replace(repr(old_specs), repr(new_specs), 1)
for old, new in [('commercial61-native-060', 'commercial61-native-061'),
                 ('build-commercial-native-060.py', 'build-commercial-native-061.py'),
                 ('commercial-hwbreak-060.py', 'commercial-hwbreak-061.py')]:
    source = source.replace(old, new)
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
