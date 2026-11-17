from pathlib import Path
import runpy

payload = runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-061.py')))['payload']
payload = payload.replace('commercial61-native-061', 'commercial61-native-062').replace('COMMERCIAL061', 'COMMERCIAL062').replace('ordered_chain_equals_full_061', 'ordered_chain_equals_full_062')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
