from pathlib import Path
import runpy

base = Path(__file__).resolve().parent
source = runpy.run_path(str(base/'build-commercial-overlay-092.py'))['source']
source = source.replace('commercial61-native-092', 'commercial61-native-093').replace('commercial61-native-091', 'commercial61-native-092')
anchor = "assert set(patch) == {'native-target/commercial-desktop077.sh', 'early-hardware092.sh', 'early-sys092'}"
assert source.count(anchor) == 1
source = source.replace(anchor, "assert set(patch) == {'native-target/commercial-desktop077.sh', 'early-hardware093.sh'}")
source = source.replace('ordered_chain_equals_full_092', 'ordered_chain_equals_full_093')
anchor = "['commercial61-native-093/initrd.img']"
assert source.count(anchor) == 1
source = source.replace(anchor, "['commercial61-native-092/early093.img']")
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
