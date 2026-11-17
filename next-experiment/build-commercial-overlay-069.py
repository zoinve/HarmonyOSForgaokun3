from pathlib import Path
import runpy

payload = runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-068.py')))['payload']
payload = payload.replace('commercial61-native-068', 'commercial61-native-069').replace(
    'COMMERCIAL068', 'COMMERCIAL069').replace('ordered_chain_equals_full_068', 'ordered_chain_equals_full_069')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
