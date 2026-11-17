from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = runpy.run_path(str(b / 'build-commercial-overlay-082.py'))['source']
source = source.replace('commercial61-native-082', 'commercial61-native-083').replace(
    'commercial61-native-081', 'commercial61-native-082')
old = "assert 'init' in patch and all(n == 'init' or n == 'network082' or n.startswith('network082/') for n in patch)"
assert source.count(old) == 1
source = source.replace(old, "assert set(patch) == {'init', 'network083-control', 'native-target/network083', 'native-target/network083/wpa.conf'}", 1)
source = source.replace('ordered_chain_equals_full_082', 'ordered_chain_equals_full_083')

if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
