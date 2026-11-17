from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = runpy.run_path(str(b / 'build-commercial-overlay-085.py'))['source']
source = source.replace('commercial61-native-085', 'commercial61-native-086').replace('commercial61-native-084', 'commercial61-native-085')
old = "assert set(patch) == {'init', 'network085-control'}"
assert source.count(old) == 1
source = source.replace(old, "assert set(patch) == {'init', 'network086-control', 'native-target/commercial-desktop077.sh'}", 1)
source = source.replace('ordered_chain_equals_full_085', 'ordered_chain_equals_full_086')

if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
