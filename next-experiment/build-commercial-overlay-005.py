"""Exhaustively compare all entries; add only the small original-context observer."""
from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-002.py')))['payload']
payload=payload.replace('commercial61-native-002','commercial61-native-005')
payload=payload.replace('assert old.keys()==new.keys()',"assert set(new)-set(old)=={'native-target/samgr-observe','native-target/samgr_standard005.cfg'} and not set(old)-set(new)")
payload=payload.replace('changed={n for n in old if old[n]!=new[n]}','changed={n for n in new if old.get(n)!=new[n]}')
payload=payload.replace("assert changed=={'init','native-target/bootstrap'},changed","assert changed=={'init','native-target/bootstrap','native-target/samgr-observe','native-target/samgr_standard005.cfg'},changed")
payload=payload.replace("member('TRAILER!!!',0,b'',3)","member('TRAILER!!!',0,b'',len(changed)+1)")
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)
