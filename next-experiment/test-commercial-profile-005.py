"""Compilation/contract check only; original-service runtime needs its own bounded boot."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
assert (base/'build-commercial-profile-005.py').is_file(),'missing original-context profile observer'
p=runpy.run_path(str(base/'build-commercial-profile-005.py'))
s=(base/'commercial-profile-005.c').read_text()
assert 'GetCfgFiles' in s and 'GetCfgDirList' in s and 'const.cust.config_dir_layer' in s
assert 'execv("/system/bin/samgr",argv)' in s
assert all(x not in s for x in ['setuid(', 'setgid(', 'setgroups(', 'setcon(', 'RegisterSystemAbility'])
if __name__=='__main__':
 check=r'''
from pathlib import Path
import json,hashlib,subprocess
w=Path('/home/zoinve/harmony-virgl-883/commercial-profile-005')
r=json.loads((w/'result.json').read_text())
assert hashlib.sha256((w/'samgr-observe').read_bytes()).hexdigest()==r['sha256']
d=subprocess.check_output(['readelf','-d',str(w/'samgr-observe')],text=True)
needed=[x.split('[')[1].split(']')[0] for x in d.splitlines() if '(NEEDED)' in x]
assert needed==['libc.so'],needed
print('PASS: observer links only libc; no supplied SDK runtime library or identity replacement')
'''
 raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=check,text=True).returncode)
