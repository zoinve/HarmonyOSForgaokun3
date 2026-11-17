from pathlib import Path
import runpy

base = Path(__file__).resolve().parent
source = runpy.run_path(str(base / 'build-commercial-overlay-087.py'))['source']
source = source.replace('commercial61-native-087', 'commercial61-native-088').replace('commercial61-native-086', 'commercial61-native-087')
anchor = "assert set(patch) == {'init'}"
assert source.count(anchor) == 1
source = source.replace(anchor, "assert set(patch) == {'native-target/appdata-sandbox019.json', 'native-target/commercial-desktop077.sh'}", 1)
source = source.replace('ordered_chain_equals_full_087', 'ordered_chain_equals_full_088')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
