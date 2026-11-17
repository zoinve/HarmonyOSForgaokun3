"""Normalize an already granted library view; retain original seccomp and AppSpawn."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-commercial-native-018.py'))
inner=p['inner']
anchor='static void commercial_graphics016(void)'
end=inner.index(anchor);before=inner[:end];close=before.rfind('}\n')
assert close>=0
before=before[:close]+'    commercial_copy005("/appdata-sandbox019.json","/run/commercial-system005/upper/etc/sandbox/appdata-sandbox.json",0644);\n'+before[close:]
inner=before+inner[end:]
outer=p['outer'].replace('commercial61-native-018-%s','commercial61-native-019-%s').replace('COMMERCIAL018','COMMERCIAL019')
payload=p['payload'].replace('inner='+repr(p['inner']),'inner='+repr(inner),1).replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
payload=payload.replace('commercial61-native-018','commercial61-native-019')
extra=r'''
image=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')
original=json.loads(subprocess.check_output(['debugfs','-R','cat /system/etc/sandbox/appdata-sandbox.json',str(image)],stderr=subprocess.PIPE))
alias=runpy.run_path(str(base/'commercial-app-sandbox-019.py'))['repair'](original)
key='native-target/appdata-sandbox019.json'
assert key not in entries
entries[key]=(stat.S_IFREG|0o644,json.dumps(alias,indent=2).encode())
for name,value in [('original-appdata-sandbox.json',original),('alias-appdata-sandbox.json',alias)]:
 (local/name).open('x').write(json.dumps(value,indent=2))
'''
anchor="entries=runpy.run_path(str(base/'commercial-archive-017.py'))['complete'](entries)"
assert payload.count(anchor)==1
payload=payload.replace(anchor,extra+'\n'+anchor,1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
