from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = runpy.run_path(str(b / 'build-commercial-overlay-077.py'))['source']
source = source.replace('commercial61-native-077', 'commercial61-native-078').replace('commercial61-native-076', 'commercial61-native-077')
source = source.replace('ordered_chain_equals_full_077', 'ordered_chain_equals_full_078')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
