from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-030.py')))['payload']
payload=payload.replace('commercial61-native-030','commercial61-native-031').replace('ordered_chain_equals_full_030','ordered_chain_equals_full_031')
payload=payload.replace("work=root/'commercial61-native-031-r2';","work=root/'commercial61-native-031';",1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)
