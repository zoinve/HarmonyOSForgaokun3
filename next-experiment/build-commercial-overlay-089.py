from pathlib import Path
import runpy

base = Path(__file__).resolve().parent
source = runpy.run_path(str(base / 'build-commercial-overlay-088.py'))['source']
source = source.replace('commercial61-native-088', 'commercial61-native-089').replace('commercial61-native-087', 'commercial61-native-088')
anchor = "assert set(patch) == {'native-target/appdata-sandbox019.json', 'native-target/commercial-desktop077.sh'}"
assert source.count(anchor) == 1
source = source.replace(anchor, "assert set(patch) == {'native-target/commercial-desktop077.sh'}", 1)
source = source.replace('ordered_chain_equals_full_088', 'ordered_chain_equals_full_089')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
