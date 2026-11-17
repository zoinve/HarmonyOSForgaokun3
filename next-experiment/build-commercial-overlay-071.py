from pathlib import Path
import runpy

payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-070.py')))['payload']
payload=payload.replace('commercial61-native-070','commercial61-native-071').replace(
    'COMMERCIAL070','COMMERCIAL071').replace('ordered_chain_equals_full_070','ordered_chain_equals_full_071')
if __name__=='__main__':
    exec(compile(payload,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
