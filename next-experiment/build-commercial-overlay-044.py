from pathlib import Path
import runpy

payload = runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-043.py')))['payload']
payload = payload.replace('commercial61-native-043', 'commercial61-native-044').replace('COMMERCIAL043', 'COMMERCIAL044').replace('ordered_chain_equals_full_043', 'ordered_chain_equals_full_044').replace('libcommercial_rs_observer043.so', 'libcommercial_rs_observer044.so')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
