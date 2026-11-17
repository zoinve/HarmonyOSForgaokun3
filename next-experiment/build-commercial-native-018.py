"""Replace only the Kirin AppSpawn hardware launcher, retaining original argv."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-commercial-native-017.py'))
inner=p['inner']
anchor='static void commercial_graphics016(void)'
end=inner.index(anchor)
before=inner[:end]
close=before.rfind('}\n')
assert close>=0
before=before[:close]+'    commercial_copy005("/graphics016/system/bin/l410_launch_appspawn_r18_namespace.sh","/run/commercial-system005/upper/bin/l410_launch_appspawn_r18_namespace.sh",0755);\n'+before[close:]
inner=before+inner[end:]
outer=p['outer'].replace('commercial61-native-017-%s','commercial61-native-018-%s').replace('COMMERCIAL017','COMMERCIAL018')
payload=p['payload'].replace('inner='+repr(p['inner']),'inner='+repr(inner),1).replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
payload=payload.replace('commercial61-native-017','commercial61-native-018')
extra=r'''
original_image=Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img')
original=subprocess.check_output(['debugfs','-R','cat /system/bin/l410_launch_appspawn_r18_namespace.sh',str(original_image)],stderr=subprocess.PIPE).decode()
launcher=runpy.run_path(str(base/'commercial-appspawn-018.py'))['repair'](original)
key='native-target/graphics016/system/bin/l410_launch_appspawn_r18_namespace.sh'
assert key not in entries
entries[key]=(stat.S_IFREG|0o755,launcher.encode())
(local/'original-appspawn-launcher.sh').open('x').write(original)
(local/'matebook-appspawn-launcher.sh').open('x').write(launcher)
'''
anchor="entries=runpy.run_path(str(base/'commercial-archive-017.py'))['complete'](entries)"
assert payload.count(anchor)==1
payload=payload.replace(anchor,extra+'\n'+anchor,1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
