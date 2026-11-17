from pathlib import Path
import runpy

base = Path(__file__).resolve().parent
source = runpy.run_path(str(base/'build-commercial-overlay-091.py'))['source']
source = source.replace('commercial61-native-091', 'commercial61-native-092').replace('commercial61-native-090', 'commercial61-native-091')
anchor = "assert set(patch) == {'native-target/commercial-desktop077.sh', 'native-target/native-hardware091'}"
assert source.count(anchor) == 1
source = source.replace(anchor, "assert set(patch) == {'native-target/commercial-desktop077.sh', 'early-hardware092.sh', 'early-sys092'}")
source = source.replace('ordered_chain_equals_full_091', 'ordered_chain_equals_full_092')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
