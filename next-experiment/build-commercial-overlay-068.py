from pathlib import Path
import runpy

payload = runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-067.py')))['payload']
payload = payload.replace('commercial61-native-067', 'commercial61-native-068').replace(
    'COMMERCIAL067', 'COMMERCIAL068').replace('ordered_chain_equals_full_067', 'ordered_chain_equals_full_068')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
