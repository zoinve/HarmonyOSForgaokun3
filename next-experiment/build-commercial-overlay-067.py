from pathlib import Path
import runpy

payload = runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-066.py')))['payload']
payload = payload.replace('commercial61-native-066', 'commercial61-native-067').replace(
    'COMMERCIAL066', 'COMMERCIAL067').replace('ordered_chain_equals_full_066', 'ordered_chain_equals_full_067')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
