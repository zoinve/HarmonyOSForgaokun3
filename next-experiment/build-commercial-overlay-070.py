from pathlib import Path
import runpy

payload = runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-069.py')))['payload']
payload = payload.replace('commercial61-native-069','commercial61-native-070').replace(
    'COMMERCIAL069','COMMERCIAL070').replace('ordered_chain_equals_full_069','ordered_chain_equals_full_070')
anchor = 'assert set(patch)=='
assert payload.count(anchor) == 1
payload = payload.replace(anchor, "resource_members070={n for n in new if n.startswith('native-target/original-ui070')}\nassert resource_members070\nassert set(patch)-resource_members070==", 1)
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__':'__main__','__file__':__file__})
