from pathlib import Path
import runpy

payload = runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-063.py')))['payload']
payload = payload.replace('commercial61-native-063', 'commercial61-native-064').replace('COMMERCIAL063', 'COMMERCIAL064').replace('ordered_chain_equals_full_063', 'ordered_chain_equals_full_064')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
