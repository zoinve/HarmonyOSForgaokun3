from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-037.py')))['payload'].replace("commercial61-native-037","commercial61-native-038").replace("commercial-return-audit-037","commercial-return-audit-038").replace("COMMERCIAL037","COMMERCIAL038").replace("ordered_chain_equals_full_037","ordered_chain_equals_full_038").replace("Reference namespace corrected startup 037","Post first-flush capture 038")
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)
