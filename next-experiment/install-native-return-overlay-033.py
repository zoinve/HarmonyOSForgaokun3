"""Install a small last-initramfs overlay; no existing EFI file is changed."""
from pathlib import Path
import base64,hashlib,json,subprocess
base=Path(__file__).resolve().parent.parent
report=base/'reports/native-original-graphics-boot-033'
blob=subprocess.check_output(['wsl','-d','Debian','--','cat','/home/zoinve/harmony-virgl-883/native-original-graphics-boot-033/return-overlay.img'])
expected=json.loads((report/'return-overlay-result.json').read_text())
assert hashlib.sha256(blob).hexdigest()==expected['overlay_sha256']
payload='blob='+repr(base64.b64encode(blob).decode())+'\n'+r'''
from pathlib import Path
import os,base64,hashlib,json,subprocess,shutil
esp=Path('/boot/efi');dest=esp/'native-original-graphics-033'
entry=esp/'loader/entries/native-original-graphics-033.conf'
root=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/native-original-graphics-boot-033')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cmd(a):return subprocess.check_output(a,text=True,timeout=30)
assert cmd(['findmnt','-n','-o','SOURCE,FSTYPE','--target',str(esp)]).split()==['/dev/nvme0n1p1','vfat']
assert cmd(['blkid','-s','PARTUUID','-o','value','/dev/nvme0n1p1']).strip()=='922f37b2-3474-4761-a370-5aa1dcd7c476'
default='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
status=cmd(['bootctl','status','--no-pager'])
assert 'Default Entry: '+default in status and 'OneShot Entry:' not in status
assert cmd(['systemctl','is-active','harmony-lab-screen-off-001.timer']).strip()=='active'
assert not dest.exists() and not entry.exists()
assert sha(esp/'native-original-graphics-032/initrd.img')=='78049c130b3ab1dcd8f29d192b168bed3681d16a8aa9c298e6b548987e51f8ad'
assert sha(esp/'native-original-graphics-031/linux')=='6fa44a5f1996a82bc95e8c44b3d32a69cc14d3789e39cffa2fcafafb7c294ff5'
assert sha(esp/'native-original-graphics-031/sc8280xp-huawei-gaokun3.dtb')=='5f6b1fa73d8bffa1984710d52c0babc4df297cbb90d9f4d9a48a433a104fb016'
data=base64.b64decode(blob)
assert hashlib.sha256(data).hexdigest()=='e90f60b8171e9a1e2ce6128d473b822a2c7a60d7dcbc831bd5ab6b291b3f6f65'
assert shutil.disk_usage(esp).free>len(data)+32*1024**2
before={str(p.relative_to(esp)):sha(p) for p in esp.rglob('*') if p.is_file()}
firmware=cmd(['efibootmgr','-v'])
with (root/'return-installation-journal.json').open('x') as f:
 json.dump(dict(efi_before=before,firmware_before=firmware,default=default),f,indent=2);f.flush();os.fsync(f.fileno())
dest.mkdir()
with (dest/'return-overlay.img').open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
text=(esp/'loader/entries/native-original-graphics-032.conf').read_text()
text=text.replace('HarmonyOS 032 - Touchpad cursor - NO AUTO REBOOT','HarmonyOS 033 - Cursor test - AUTO RETURN 7 MIN')
text=text.replace('options rdinit=', 'initrd /native-original-graphics-033/return-overlay.img\noptions rdinit=')
text=text.replace('panic=0','panic=15')
assert text.count('\ninitrd ')==2
with entry.open('x') as f:f.write(text);f.flush();os.fsync(f.fileno())
os.sync()
for n,h in before.items():assert sha(esp/n)==h,n
assert cmd(['efibootmgr','-v'])==firmware
assert 'Default Entry: '+default in cmd(['bootctl','status','--no-pager'])
r=dict(entry=str(entry),entry_text=text,overlay_sha256=sha(dest/'return-overlay.img'),old_efi_files_unchanged=len(before),
 free_bytes=shutil.disk_usage(esp).free,ubuntu_default_unchanged=True,one_shot_selected=False,reboot_requested=False,
 target_budget_seconds=240,outer_fallback_seconds=420,hardware_watchdog=False,runtime_verified=False)
with (root/'return-installation-result.json').open('x') as f:json.dump(r,f,indent=2)
print(json.dumps(r,indent=2))
'''
if __name__=='__main__':
 r=subprocess.run(['ssh','matebook','sudo -n python3 -'],input=payload,text=True,capture_output=True,timeout=120)
 with (report/'return-installation.stdout').open('x') as f:f.write(r.stdout)
 with (report/'return-installation.stderr').open('x') as f:f.write(r.stderr)
 r.check_returncode()
 with (report/'return-installation-result.json').open('x') as f:json.dump(json.loads(r.stdout),f,indent=2)
 print(r.stdout)
