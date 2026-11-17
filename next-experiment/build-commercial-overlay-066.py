from pathlib import Path
import runpy

payload = runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-065.py')))['payload']
payload = payload.replace('commercial61-native-065', 'commercial61-native-066').replace('COMMERCIAL065', 'COMMERCIAL066').replace('ordered_chain_equals_full_065', 'ordered_chain_equals_full_066')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
