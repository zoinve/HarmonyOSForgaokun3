from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-031.py')))['payload']
payload=payload.replace('commercial61-native-031','commercial61-native-032').replace('ordered_chain_equals_full_031','ordered_chain_equals_full_032')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)
