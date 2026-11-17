from pathlib import Path

b = Path(__file__).resolve().parent
source = (b / 'build-commercial-overlay-075.py').read_text()
# Execute the underlying exact-delta builder, not the 075 wrapper's transformation.
import runpy
source = runpy.run_path(str(b / 'build-commercial-overlay-075.py'))['source']
source = source.replace('commercial61-native-075', 'commercial61-native-076').replace('commercial61-native-074', 'commercial61-native-075')
start = source.index('assert set(patch) == ')
end = source.index('\nassert dict(before, **patch)', start)
source = source[:start] + '''assert set(patch) == {'init', 'native-target/samgr_standard005.cfg',
    'native-target/commercial-direct-desktop-075.sh'}''' + source[end:]
source = source.replace('ordered_chain_equals_full_075', 'ordered_chain_equals_full_076')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
