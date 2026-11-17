from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = runpy.run_path(str(b / 'build-commercial-overlay-079.py'))['source']
source = source.replace('commercial61-native-079', 'commercial61-native-080').replace('commercial61-native-078', 'commercial61-native-079')
start = source.index('expected079=')
end = source.index('\nassert dict(before, **patch)', start)
source = source[:start] + "assert set(patch) == {'init'}" + source[end:]
source = source.replace('ordered_chain_equals_full_079', 'ordered_chain_equals_full_080')
source = source.replace('assert len(blob) < 8 * 1024 * 1024', 'assert len(blob) < 2 * 1024 * 1024')

if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
