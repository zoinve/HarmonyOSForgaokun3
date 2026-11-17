from pathlib import Path
import runpy

base = Path(__file__).resolve().parent
source = runpy.run_path(str(base/'build-commercial-overlay-093.py'))['source']
source = source.replace('commercial61-native-093', 'commercial61-native-094').replace('early093.img', 'early094.img')
source = source.replace('ordered_chain_equals_full_093', 'ordered_chain_equals_full_094')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
