from pathlib import Path
import runpy

payload = runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-062.py')))['payload']
payload = payload.replace('commercial61-native-062', 'commercial61-native-063').replace('COMMERCIAL062', 'COMMERCIAL063').replace('ordered_chain_equals_full_062', 'ordered_chain_equals_full_063')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
