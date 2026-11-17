from pathlib import Path
import runpy

payload = runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-070.py')))['payload']
payload = payload.replace('commercial61-native-070', 'commercial61-native-072').replace(
    'COMMERCIAL070', 'COMMERCIAL072').replace('ordered_chain_equals_full_070', 'ordered_chain_equals_full_072')
anchor = 'assert set(patch)-resource_members070=='
assert payload.count(anchor) == 1
payload = payload.replace(anchor,
    "codec_members072={n for n in new if n.startswith('native-target/software-codec072')}\nassert codec_members072\nassert set(patch)-resource_members070-codec_members072==", 1)
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
