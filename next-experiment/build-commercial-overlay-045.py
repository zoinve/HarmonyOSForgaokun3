from pathlib import Path
import runpy

payload = runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-044.py')))['payload']
payload = payload.replace('commercial61-native-044', 'commercial61-native-045').replace('COMMERCIAL044', 'COMMERCIAL045').replace('ordered_chain_equals_full_044', 'ordered_chain_equals_full_045')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
