from pathlib import Path
import runpy

payload = runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-059.py')))['payload']
payload = payload.replace('commercial61-native-059', 'commercial61-native-060').replace('COMMERCIAL059', 'COMMERCIAL060').replace('ordered_chain_equals_full_059', 'ordered_chain_equals_full_060')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
