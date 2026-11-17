from pathlib import Path
import runpy

payload = runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-060.py')))['payload']
payload = payload.replace('commercial61-native-060', 'commercial61-native-061').replace('COMMERCIAL060', 'COMMERCIAL061').replace('ordered_chain_equals_full_060', 'ordered_chain_equals_full_061')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
