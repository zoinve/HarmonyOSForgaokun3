from pathlib import Path
import runpy

payload = runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-064.py')))['payload']
payload = payload.replace('commercial61-native-064', 'commercial61-native-065').replace('COMMERCIAL064', 'COMMERCIAL065').replace('ordered_chain_equals_full_064', 'ordered_chain_equals_full_065')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
