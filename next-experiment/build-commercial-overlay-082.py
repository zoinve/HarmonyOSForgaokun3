from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = runpy.run_path(str(b / 'build-commercial-overlay-081.py'))['source']
source = source.replace('commercial61-native-081', 'commercial61-native-082').replace(
    'commercial61-native-080', 'commercial61-native-081')
source = source.replace("assert set(patch) == {'init'}", "assert 'init' in patch and all(n == 'init' or n == 'network082' or n.startswith('network082/') for n in patch)")
source = source.replace('ordered_chain_equals_full_081', 'ordered_chain_equals_full_082')

if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
