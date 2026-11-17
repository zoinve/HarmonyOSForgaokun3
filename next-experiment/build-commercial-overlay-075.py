"""An exact bounded delta over retained 074; no shared payload deletion."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = (b / 'build-commercial-overlay-074.py').read_text().replace(
    'commercial61-native-074', 'commercial61-native-075').replace('commercial61-native-073', 'commercial61-native-074')
start = source.index('assert set(patch) == ')
end = source.index('\nassert dict(before, **patch)', start)
source = source[:start] + '''assert set(patch) == {'init', 'native-target/bootstrap',
    'native-target/commercial-direct-desktop-075.sh',
    'native-target/graphics016/vendor/lib64/libdisplay_composer_vdi_impl.z.so'}''' + source[end:]
source = source.replace('ordered_chain_equals_full_074', 'ordered_chain_equals_full_075')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
