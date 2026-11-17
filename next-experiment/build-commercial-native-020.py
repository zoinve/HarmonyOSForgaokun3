"""Reference-aligned normal desktop bootstrap, retaining commercial service identities."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-commercial-native-019.py'))
inner=p['inner']
end=inner.index('static void commercial_graphics016(void)')
before=inner[:end];close=before.rfind('}\n')
assert close>=0
before=before[:close]+'    commercial_copy005("/desktop-order020.sh","/run/commercial-system005/upper/bin/l410_account_first_boot_order_v1.sh",0755);\n'+before[close:]
inner=before+inner[end:]
outer=p['outer'].replace('commercial61-native-019-%s','commercial61-native-020-%s').replace('COMMERCIAL019','COMMERCIAL020')
payload=p['payload'].replace('inner='+repr(p['inner']),'inner='+repr(inner),1).replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
payload=payload.replace('commercial61-native-019','commercial61-native-020')
extra=r'''
image=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')
original=subprocess.check_output(['debugfs','-R','cat /system/bin/l410_account_first_boot_order_v1.sh',str(image)],stderr=subprocess.PIPE).decode()
patched=runpy.run_path(str(base/'commercial-desktop-order-020.py'))['repair'](original)
key='native-target/desktop-order020.sh'
assert key not in entries
entries[key]=(stat.S_IFREG|0o755,patched.encode())
(local/'original-account-order.sh').open('x').write(original)
(local/'matebook-account-order.sh').open('x').write(patched)
'''
anchor="entries=runpy.run_path(str(base/'commercial-archive-017.py'))['complete'](entries)"
assert payload.count(anchor)==1
payload=payload.replace(anchor,extra+'\n'+anchor,1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
