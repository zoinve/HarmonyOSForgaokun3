"""Actual Binder submission, endpoint state and full maps in original desktop boot."""
from pathlib import Path
import runpy
import subprocess

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-042.py'))
inner = p['inner'].replace('libcommercial_rs_observer042.so', 'libcommercial_rs_observer043.so')
inner = runpy.run_path(str(b / 'commercial-stream-observer-043.py'))['instrument'](inner)
outer = p['outer'].replace('commercial61-native-042', 'commercial61-native-043').replace('COMMERCIAL042', 'COMMERCIAL043')
payload = p['payload'].replace('inner=' + repr(p['inner']), 'inner=' + repr(inner), 1).replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1)
payload = payload.replace('commercial61-native-042', 'commercial61-native-043').replace('commercial-rs-observer-042-r3', 'commercial-rs-observer-043').replace('libcommercial_rs_observer042.so', 'libcommercial_rs_observer043.so')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
