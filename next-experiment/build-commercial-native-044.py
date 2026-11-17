"""Keep original desktop launch and bounds; observe original tokenless delivery."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-043.py'))
inner = p['inner'].replace('libcommercial_rs_observer043.so', 'libcommercial_rs_observer044.so')
outer = p['outer'].replace('commercial61-native-043', 'commercial61-native-044').replace('COMMERCIAL043', 'COMMERCIAL044')
outer = runpy.run_path(str(b / 'commercial-outer-binder-044.py'))['instrument'](outer)
payload = p['payload'].replace('inner=' + repr(p['inner']), 'inner=' + repr(inner), 1).replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1)
payload = payload.replace('commercial61-native-043', 'commercial61-native-044').replace('commercial-rs-observer-043', 'commercial-rs-observer-044').replace('libcommercial_rs_observer043.so', 'libcommercial_rs_observer044.so')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
