"""Correct only diagnostic copy source paths after the target chroot; retain failed 005 evidence."""
from pathlib import Path
import runpy,subprocess
p=runpy.run_path(str(Path(__file__).with_name('build-commercial-native-005.py')))
inner=p['inner'].replace('commercial_copy005("/native-target/samgr-observe",','commercial_copy005("/samgr-observe",').replace('commercial_copy005("/native-target/samgr_standard005.cfg",','commercial_copy005("/samgr_standard005.cfg",')
assert inner!=p['inner']
outer=p['outer'].replace('commercial61-native-005-%s','commercial61-native-006-%s').replace('COMMERCIAL005','COMMERCIAL006')
payload=p['payload'].replace('inner='+repr(p['inner']),'inner='+repr(inner),1).replace('outer='+repr(p['outer']),'outer='+repr(outer),1).replace('commercial61-native-005','commercial61-native-006')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
