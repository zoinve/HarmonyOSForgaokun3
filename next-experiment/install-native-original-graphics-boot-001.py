"""Install a counted candidate, preserving Ubuntu default; never select or reboot."""
from pathlib import Path
import json
import subprocess

BASE = Path(__file__).resolve().parent.parent
PAYLOAD = r'''
from pathlib import Path
import hashlib,json,os,shutil,subprocess
def cmd(a):return subprocess.check_output(a,text=True,timeout=30)
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,d):
 with p.open('x') as f:json.dump(d,f,indent=2);f.flush();os.fsync(f.fileno())
esp=Path('/boot/efi');root=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/native-original-graphics-boot-001')
assert cmd(['findmnt','-n','-o','SOURCE,FSTYPE','--target',str(esp)]).split()==['/dev/nvme0n1p1','vfat']
assert cmd(['blkid','-s','PARTUUID','-o','value','/dev/nvme0n1p1']).strip()=='922f37b2-3474-4761-a370-5aa1dcd7c476'
default='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
assert 'Default Entry: '+default in cmd(['bootctl','status','--no-pager'])
assert cmd(['systemctl','is-active','harmony-lab-screen-off-001.timer']).strip()=='active'
before={str(p.relative_to(esp)):sha(p) for p in esp.rglob('*') if p.is_file()}
loader={str(p.relative_to(esp)):p.read_text() for p in (esp/'loader').rglob('*.conf')}
efi=cmd(['efibootmgr','-v'])
entry=esp/'loader/entries/native-original-graphics-001+1.conf';dest=esp/'native-original-graphics-001'
assert not dest.exists() and not any(entry.parent.glob('native-original-graphics-001*'))
assert not (root/'installation-result.json').exists() and not (root/'installation-journal.json').exists()
d=json.loads((root/'result.json').read_text())
for row in d['artifacts']:
 p=root/row['name'];assert p.is_file() and not p.is_symlink() and sha(p)==row['sha256']
kernel=esp/'harmony-native-diag-015/linux';dtb=esp/'harmony-native-diag-015/sc8280xp-huawei-gaokun3.dtb'
assert sha(kernel)==sha(root/'linux') and sha(dtb)==sha(root/'sc8280xp-huawei-gaokun3.dtb')
# Only two obsolete, byte-identical and unreferenced kernel cache copies.
obsolete=[esp/f'harmony-native-diag-{n}/linux' for n in ['009','010']]
for p in obsolete:
 assert not p.is_symlink() and not p.parent.is_symlink() and sha(p)==sha(kernel)
 assert not any('/'+str(p.parent.relative_to(esp))+'/' in text for text in loader.values())
assert shutil.disk_usage(esp).free+sum(p.stat().st_size for p in obsolete)>(root/'initrd.img').stat().st_size+64*1024**2
save(root/'installation-journal.json',dict(efi_before=before,loader_before=loader,firmware_before=efi,
 deleted_obsolete_kernel_caches=[str(p) for p in obsolete],retained_identical_kernel=str(kernel)))
os.sync()
for p in obsolete:p.unlink()
os.sync();assert shutil.disk_usage(esp).free>(root/'initrd.img').stat().st_size+64*1024**2
dest.mkdir()
with (root/'initrd.img').open('rb') as src,(dest/'initrd.img').open('xb') as out:
 shutil.copyfileobj(src,out);out.flush();os.fsync(out.fileno())
assert sha(dest/'initrd.img')==sha(root/'initrd.img')
options='rdinit=/init harmony.diag=1 harmony.original_init_test=1 harmony.native_original=1 ohos.boot.hardware=matebookego lsm=capability,landlock,selinux security=selinux selinux=1 enforcing=0 clk_ignore_unused pd_ignore_unused arm64.nopauth iommu.passthrough=0 iommu.strict=0 pcie_aspm.policy=powersupersave modprobe.blacklist=simpledrm efi=noruntime fbcon=rotate:1 usbhid.quirks=0x12d1:0x10b8:0x20000000 console=tty0 consoleblank=0 loglevel=7 panic=30'
assert not any(x in options for x in ['root=','resume=','nowatchdog','machine_id='])
text='\n'.join(['title Harmony original-service native trial 001 (experimental)','version 7.1.0-rc3-gaokun3-el2','sort-key zzzz-harmony-diagnostic','linux /harmony-native-diag-015/linux','devicetree /harmony-native-diag-015/sc8280xp-huawei-gaokun3.dtb','initrd /native-original-graphics-001/initrd.img','options '+options,''])
with entry.open('x') as f:f.write(text);f.flush();os.fsync(f.fileno())
os.sync()
deleted={str(p.relative_to(esp)) for p in obsolete}
for rel,h in before.items():
 if rel not in deleted:assert sha(esp/rel)==h,rel
assert {str(p.relative_to(esp)):p.read_text() for p in (esp/'loader').rglob('*.conf') if p!=entry}==loader
assert cmd(['efibootmgr','-v'])==efi
assert 'Default Entry: '+default in cmd(['bootctl','status','--no-pager'])
assert entry.name in cmd(['bootctl','list','--no-pager'])
result=dict(entry=str(entry),entry_text=text,existing_efi_files_unchanged=len(before)-len(deleted),
 deleted_obsolete_kernel_caches=list(deleted),free_bytes=shutil.disk_usage(esp).free,
 ubuntu_default_unchanged=True,firmware_entries_unchanged=True,one_shot_selected=False,reboot_requested=False)
save(root/'installation-result.json',result);print(json.dumps(result,indent=2))
'''

if __name__ == '__main__':
    report = BASE/'reports/native-original-graphics-boot-001/install-result.json'
    assert not report.exists()
    r = subprocess.run(['ssh','matebook','sudo -n python3 -'],input=PAYLOAD,text=True,capture_output=True,timeout=300)
    report.with_suffix('.stdout').write_text(r.stdout,encoding='utf-8')
    report.with_suffix('.stderr').write_text(r.stderr,encoding='utf-8')
    r.check_returncode()
    with report.open('x',encoding='utf-8') as f:json.dump(json.loads(r.stdout),f,indent=2)
    print(r.stdout)
