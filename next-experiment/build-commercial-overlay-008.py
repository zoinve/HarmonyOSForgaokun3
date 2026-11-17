from pathlib import Path
import runpy, subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-005.py')))['payload'].replace('commercial61-native-005','commercial61-native-008')
before="{'native-target/samgr-observe','native-target/samgr_standard005.cfg'}"
after="{'native-target/samgr-observe','native-target/samgr_standard005.cfg','native-target/sandbox-system008.json','native-target/sandbox-chipset008.json'}"
assert payload.count(before)==1
payload=payload.replace(before,after,1)
before="{'init','native-target/bootstrap','native-target/samgr-observe','native-target/samgr_standard005.cfg'}"
after="{'init','native-target/bootstrap','native-target/samgr-observe','native-target/samgr_standard005.cfg','native-target/sandbox-system008.json','native-target/sandbox-chipset008.json'}"
assert payload.count(before)==1
payload=payload.replace(before,after,1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)
