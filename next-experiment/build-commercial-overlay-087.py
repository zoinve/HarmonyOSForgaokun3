from pathlib import Path
import runpy

base = Path(__file__).resolve().parent
source = runpy.run_path(str(base / 'build-commercial-overlay-086.py'))['source']
source = source.replace('commercial61-native-086', 'commercial61-native-087').replace('commercial61-native-085', 'commercial61-native-086')
anchor = "assert set(patch) == {'init', 'network086-control', 'native-target/commercial-desktop077.sh'}"
assert source.count(anchor) == 1
source = source.replace(anchor, "assert set(patch) == {'init'}", 1)
source = source.replace('ordered_chain_equals_full_086', 'ordered_chain_equals_full_087')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
