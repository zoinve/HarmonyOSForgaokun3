from pathlib import Path
import runpy

payload = runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-045.py')))['payload']
payload = payload.replace('commercial61-native-045', 'commercial61-native-046').replace('COMMERCIAL045', 'COMMERCIAL046').replace('ordered_chain_equals_full_045', 'ordered_chain_equals_full_046')
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
