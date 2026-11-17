from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-041.py')))['payload'].replace("commercial61-native-041","commercial61-native-042").replace("commercial-return-audit-041","commercial-return-audit-042").replace("COMMERCIAL041","COMMERCIAL042").replace("ordered_chain_equals_full_041","ordered_chain_equals_full_042").replace("libcommercial_rs_observer041.so","libcommercial_rs_observer042.so").replace("Original application transaction observation 041","Original transaction mode and state 042")
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)
