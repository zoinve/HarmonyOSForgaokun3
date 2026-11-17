from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-036.py')))['payload'].replace("commercial61-native-036","commercial61-native-037").replace("commercial-return-audit-036","commercial-return-audit-037").replace("COMMERCIAL036","COMMERCIAL037").replace("ordered_chain_equals_full_036","ordered_chain_equals_full_037").replace("Reference service startup 036","Reference namespace corrected startup 037")
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)
