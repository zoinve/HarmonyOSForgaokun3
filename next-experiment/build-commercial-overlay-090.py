from pathlib import Path
import runpy

base = Path(__file__).resolve().parent
source = runpy.run_path(str(base / 'build-commercial-overlay-089.py'))['source']
source = source.replace('commercial61-native-089', 'commercial61-native-090').replace('commercial61-native-088', 'commercial61-native-089')
source = source.replace('ordered_chain_equals_full_089', 'ordered_chain_equals_full_090')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
