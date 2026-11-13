"""Add one isolated systemd-boot diagnostic entry; never select it or reboot."""
from pathlib import Path
import json
import subprocess

base = Path(__file__).resolve().parent.parent
preflight = json.loads((base / 'reports/baremetal-boot-entry-preflight-001.json').read_text())
assert preflight['boot']['returncode'] == 0
assert 'systemd-boot' in preflight['boot']['stdout']
assert 'Ubuntu 26.04 (standard kernel)' in preflight['boot']['stdout']
report = base / 'reports/baremetal-boot-entry-installed-001.json'
assert not report.exists()
payload = 'expected_loader = ' + repr(preflight['loader_files']) + '\n'
payload += 'expected_efi = ' + repr(preflight['efi']['stdout']) + '\n'
payload += r'''
from pathlib import Path
import hashlib,json,os,shutil,subprocess

def command(args):
    return subprocess.check_output(args,text=True,timeout=30)

def digest(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()

lab=Path('/mnt/harmony-lab/work')
assert command(['findmnt','-n','-o','SOURCE,UUID','--target',str(lab)]).split()==['/dev/nvme0n1p4','00029cdd-1748-4d2f-b73b-8e8164922098']
esp=Path('/boot/efi')
assert command(['findmnt','-n','-o','SOURCE,FSTYPE','--target',str(esp)]).split()==['/dev/nvme0n1p1','vfat']
assert command(['blkid','-s','PARTUUID','-o','value','/dev/nvme0n1p1']).strip()=='922f37b2-3474-4761-a370-5aa1dcd7c476'
assert command(['efibootmgr','-v'])==expected_efi
assert {str(p):p.read_text() for p in (esp/'loader').rglob('*.conf')}==expected_loader
entry=esp/'loader/entries/harmony-native-diag-004+1.conf'
dest=esp/'harmony-native-diag-004'
backup=lab/'boot-entry-install-001'
assert not dest.exists() and not entry.exists() and not backup.exists()
assert not any((esp/'loader/entries').glob('harmony-native-diag-004*'))
sources={
 'linux':(lab/'native-build-001/artifacts/arch/arm64/boot/Image','f304d26414e27122716d8b6199c0d096bb314d80dc5f32fa3300dd97420523d0'),
 'sc8280xp-huawei-gaokun3.dtb':(lab/'native-build-001/artifacts/arch/arm64/boot/dts/qcom/sc8280xp-huawei-gaokun3.dtb','2cfe996199fc203abaa0e0fad535e67e6af336b50c168119345d5678248cee32'),
 'initrd.img':(lab/'native-diagnostic-init-004/diagnostic-init.cpio.gz','884772104ac2f858697a1730d0f8307db05a9155c3b677355f881c1939b120e1')}
for source,sha in sources.values(): assert source.is_file() and digest(source)==sha
assert shutil.disk_usage(esp).free>sum(p.stat().st_size for p,_ in sources.values())+64*1024**2
# Protect every existing EFI file, not just the two Ubuntu entries.
before={str(p.relative_to(esp)):digest(p) for p in esp.rglob('*') if p.is_file()}
backup.mkdir()
(backup/'efi-files-before.json').write_text(json.dumps(before,indent=2))
(backup/'loader-config-before.json').write_text(json.dumps(expected_loader,indent=2))
(backup/'efibootmgr-before.txt').write_text(expected_efi)
os.sync()
dest.mkdir()
copied=[]
for name,(source,sha) in sources.items():
    target=dest/name
    with source.open('rb') as src,target.open('xb') as dst:
        shutil.copyfileobj(src,dst)
        dst.flush();os.fsync(dst.fileno())
    assert digest(target)==sha and digest(source)==sha
    copied.append(dict(path=str(target),sha256=sha,bytes=target.stat().st_size))
# Keep board workarounds from the known Ubuntu entry, but no host root,
# resume target, machine identity, SELinux relaxation or watchdog bypass.
options='rdinit=/init harmony.diag=1 clk_ignore_unused pd_ignore_unused arm64.nopauth iommu.passthrough=0 iommu.strict=0 pcie_aspm.policy=powersupersave modprobe.blacklist=simpledrm efi=noruntime fbcon=rotate:1 usbhid.quirks=0x12d1:0x10b8:0x20000000 console=tty0 consoleblank=0 loglevel=7 panic=30'
text='\n'.join([
 'title Harmony lab - native hardware diagnostic 004 (NOT HarmonyOS)',
 'version 7.1.0-rc3-gaokun3-el2',
 'sort-key zzzz-harmony-diagnostic',
 'linux /harmony-native-diag-004/linux',
 'devicetree /harmony-native-diag-004/sc8280xp-huawei-gaokun3.dtb',
 'initrd /harmony-native-diag-004/initrd.img',
 'options '+options,''])
assert options.split().count('harmony.diag=1')==1
assert not any(s in options for s in ['root=','resume=','machine_id=','enforcing=0','nowatchdog'])
with entry.open('x') as stream:
    stream.write(text);stream.flush();os.fsync(stream.fileno())
os.sync()
assert entry.read_text()==text
for rel,sha in before.items(): assert digest(esp/rel)==sha,rel
assert {str(p):p.read_text() for p in (esp/'loader').rglob('*.conf') if p!=entry}==expected_loader
assert command(['efibootmgr','-v'])==expected_efi
listing=command(['bootctl','list','--no-pager'])
assert entry.name in listing
status=command(['bootctl','status','--no-pager'])
assert 'Default Entry: 8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf' in status
(backup/'bootctl-list-after.txt').write_text(listing)
(backup/'bootctl-status-after.txt').write_text(status)
result=dict(entry=str(entry),entry_text=text,artifacts=copied,existing_efi_files_verified_unchanged=len(before),ubuntu_default_unchanged=True,firmware_boot_entries_unchanged=True,boot_counting_attempts=1,one_shot_selected=False,reboot_requested=False,native_boot_attempted=False,harmony_compatibility_verified=False)
(backup/'installation-result.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
'''
compile(payload, 'remote-install-entry', 'exec')
if __name__ == '__main__':
    r = subprocess.run(['ssh', 'matebook', 'sudo -n python3 -'], input=payload,
                       text=True, capture_output=True, timeout=300)
    (base / 'reports/baremetal-boot-entry-install-001.stdout').write_text(r.stdout, encoding='utf-8')
    (base / 'reports/baremetal-boot-entry-install-001.stderr').write_text(r.stderr, encoding='utf-8')
    r.check_returncode()
    result = json.loads(r.stdout)
    report.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
