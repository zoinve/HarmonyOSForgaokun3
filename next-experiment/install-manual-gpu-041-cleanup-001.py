"""Back up old Harmony menu entries, retain Ubuntu and all kernel/image evidence."""
from pathlib import Path
import base64, hashlib, json, subprocess
project = Path(__file__).resolve().parent.parent
report = project / 'reports/manual-gpu-041-boot-cleanup-001'
expected = json.loads((report / 'result.json').read_text())
blob = subprocess.check_output(['wsl', '-d', 'Debian', '--', 'cat',
    '/home/zoinve/harmony-virgl-883/manual-gpu-041-boot-cleanup-001/manual-gpu-overlay.img'])
assert hashlib.sha256(blob).hexdigest() == expected['overlay_sha256']
payload = 'blob=' + repr(base64.b64encode(blob).decode()) + '\n' + r'''
from pathlib import Path
import base64, hashlib, json, os, shutil, subprocess
esp=Path('/boot/efi'); entries=esp/'loader/entries'
root=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/manual-gpu-041-boot-cleanup-001')
dest=esp/'harmonyos-gpu-manual'; entry=entries/'harmonyos-gpu-manual.conf'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def cmd(a):return subprocess.check_output(a,text=True,timeout=30)
def write_new(p,data):
 with p.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
assert cmd(['findmnt','-n','-o','SOURCE,FSTYPE','--target',str(esp)]).split()==['/dev/nvme0n1p1','vfat']
default='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
status=cmd(['bootctl','status','--no-pager'])
assert 'Current Entry: '+default in status and 'Default Entry: '+default in status
assert 'OneShot Entry:' not in status
assert cmd(['systemctl','is-active','harmony-lab-screen-off-001.timer']).strip()=='active'
assert not root.exists() and not dest.exists() and not entry.exists()
required={'native-original-graphics-031/linux':'6fa44a5f1996a82bc95e8c44b3d32a69cc14d3789e39cffa2fcafafb7c294ff5',
 'native-original-graphics-031/sc8280xp-huawei-gaokun3.dtb':'5f6b1fa73d8bffa1984710d52c0babc4df297cbb90d9f4d9a48a433a104fb016',
 'native-original-graphics-032/initrd.img':'78049c130b3ab1dcd8f29d192b168bed3681d16a8aa9c298e6b548987e51f8ad'}
for n,h in required.items():assert sha(esp/n)==h,n
data=base64.b64decode(blob)
assert hashlib.sha256(data).hexdigest()=='74e23840e0dfc57d94e23791dac8935b78905cc12e8be1fe6b17981c6312886d'
assert shutil.disk_usage(esp).free>len(data)+32*1024**2
old=sorted(entries.glob('native-original-graphics-*.conf'))
assert old and all('Harmony' in p.read_text() for p in old)
source=(entries/'native-original-graphics-032.conf').read_text()
text=source.replace('title HarmonyOS 032 - Touchpad cursor - NO AUTO REBOOT',
 'title HarmonyOS - GPU accelerated - MANUAL EXIT (no auto reboot)')
assert text!=source and 'panic=0' in text and 'panic=15' not in text
text=text.replace('options rdinit=', 'initrd /harmonyos-gpu-manual/manual-gpu-overlay.img\noptions rdinit=')
assert text.count('\ninitrd ')==2
before={str(p.relative_to(esp)):sha(p) for p in esp.rglob('*') if p.is_file()}
firmware=cmd(['efibootmgr','-v']); loader=(esp/'loader/loader.conf').read_bytes()
root.mkdir(); backup=root/'archived-entries'; backup.mkdir()
journal=dict(efi_before=before,firmware_before=firmware,default=default,
 archived_entries=[str(p.relative_to(esp)) for p in old],new_entry_text=text,
 boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip())
write_new(root/'before.json',json.dumps(journal,indent=2).encode())
for p in old:
 write_new(backup/p.name,p.read_bytes());assert sha(backup/p.name)==sha(p)
os.sync()
dest.mkdir();write_new(dest/'manual-gpu-overlay.img',data)
assert sha(dest/'manual-gpu-overlay.img')==hashlib.sha256(data).hexdigest()
write_new(entry,text.encode());assert entry.read_text()==text
for p in old:
 assert sha(p)==sha(backup/p.name)
 p.unlink()
os.sync()
removed=set(journal['archived_entries'])
for n,h in before.items():
 if n in removed:assert not (esp/n).exists() and sha(backup/Path(n).name)==h
 else:assert sha(esp/n)==h,n
assert (esp/'loader/loader.conf').read_bytes()==loader
assert cmd(['efibootmgr','-v'])==firmware
assert 'Default Entry: '+default in cmd(['bootctl','status','--no-pager'])
assert not list(entries.glob('native-original-graphics-*.conf'))
assert [p.name for p in entries.glob('*.conf') if 'Harmony' in p.read_text()]==[entry.name]
r=dict(entry=str(entry),entry_text=text,archived_entry_count=len(old),backup=str(backup),
 other_efi_files_unchanged=len(before)-len(old),kernel_images_deleted=False,
 ubuntu_default_unchanged=True,firmware_unchanged=True,automatic_exit=False,
 original_manual_032_init=True,original_gpu_041_composer=True,
 reboot_requested=False,one_shot_selected=False,runtime_boot_tested=False,
 free_bytes=shutil.disk_usage(esp).free,remaining_entries=sorted(p.name for p in entries.glob('*.conf')))
write_new(root/'result.json',json.dumps(r,indent=2).encode())
print(json.dumps(r,indent=2))
'''
if __name__ == '__main__':
    r = subprocess.run(['ssh', 'matebook', 'sudo -n python3 -'], input=payload,
                       text=True, capture_output=True, timeout=120)
    for name, value in [('installation.stdout', r.stdout), ('installation.stderr', r.stderr)]:
        with (report / name).open('x') as f: f.write(value)
    r.check_returncode()
    with (report / 'installation-result.json').open('x') as f: json.dump(json.loads(r.stdout), f, indent=2)
    print(r.stdout)
