from pathlib import Path
import runpy

payload = runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-042.py')))['payload']
payload = payload.replace('commercial61-native-042', 'commercial61-native-043').replace('COMMERCIAL042', 'COMMERCIAL043').replace('ordered_chain_equals_full_042', 'ordered_chain_equals_full_043').replace('libcommercial_rs_observer042.so', 'libcommercial_rs_observer043.so')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
