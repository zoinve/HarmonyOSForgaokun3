from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
source = runpy.run_path(str(b / 'build-commercial-overlay-076.py'))['source']
source = source.replace('commercial61-native-076', 'commercial61-native-077').replace('commercial61-native-075', 'commercial61-native-076')
start = source.index('assert set(patch) == ')
end = source.index('\nassert dict(before, **patch)', start)
source = source[:start] + "assert set(patch) == {'init', 'native-target/samgr_standard005.cfg', 'native-target/commercial-desktop077.sh'}" + source[end:]
source = source.replace('ordered_chain_equals_full_076', 'ordered_chain_equals_full_077')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
