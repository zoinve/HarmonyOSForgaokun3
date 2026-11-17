from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = runpy.run_path(str(b / 'build-commercial-overlay-080.py'))['source']
source = source.replace('commercial61-native-080', 'commercial61-native-081').replace('commercial61-native-079', 'commercial61-native-080')
source = source.replace('ordered_chain_equals_full_080', 'ordered_chain_equals_full_081')

if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
