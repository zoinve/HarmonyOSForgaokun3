"""Archive and remove only three unreferenced, hash-known oldest diagnostic assets."""
from pathlib import Path
import json
import subprocess

base=Path(__file__).resolve().parent.parent
out=base/'reports/baremetal-efi-assets-archive-001.json'
assert not out.exists()
audit=json.loads((base/'reports/baremetal-efi-space-audit-001.json').read_text())
expected={}
for number,candidate in [('001','004')]:
    installed=json.loads((base/f'reports/baremetal-boot-entry-installed-{number}.json').read_text())
    for row in installed['artifacts']:
        name=str(Path(row['path'])).replace('\\','/').removeprefix('/boot/efi/')
        assert name.startswith(f'harmony-native-diag-{candidate}/')
        expected[name]=dict(sha256=row['sha256'],bytes=row['bytes'])
assert len(expected)==3
payload='expected='+repr(expected)+'\naudit='+repr(audit)+'\n'+r'''
from pathlib import Path
import hashlib,json,os,shutil,subprocess
esp=Path('/boot/efi');lab=Path('/mnt/harmony-lab/work')
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def command(args):return subprocess.check_output(args,text=True,timeout=30)
def configs():return {str(p):p.read_text() for p in (esp/'loader').rglob('*.conf')}
def guards():
    assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==audit['boot_id']
    assert 'harmony.diag=1' not in Path('/proc/cmdline').read_text().split()
    assert command(['findmnt','-n','-o','SOURCE,UUID','--target',str(lab)]).split()==['/dev/nvme0n1p4','00029cdd-1748-4d2f-b73b-8e8164922098']
    assert command(['findmnt','-n','-o','SOURCE,FSTYPE','--target',str(esp)]).split()==['/dev/nvme0n1p1','vfat']
    assert configs()==audit['configs'] and command(['efibootmgr','-v'])==audit['efi']
    v=Path('/sys/firmware/efi/efivars');g='4a67b082-0a4c-41cf-b6c7-440b29bb8c4f'
    assert (v/('LoaderEntryDefault-'+g)).read_bytes()[4:].decode('utf-16-le').rstrip('\0')=='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
    one=v/('LoaderEntryOneShot-'+g);assert not one.exists() or not one.read_bytes()[4:].decode('utf-16-le').rstrip('\0')
    assert not list((esp/'loader/entries').glob('harmony-native-diag-*'))
    for directory in ['harmony-native-diag-004']:
        assert not any('/'+directory+'/' in text for text in configs().values())
        p=esp/directory;assert p.is_dir() and not p.is_symlink()
        assert {str(f.relative_to(esp)) for f in p.iterdir()}=={name for name in expected if name.startswith(directory+'/')}
guards()
before={str(p.relative_to(esp)):sha(p) for p in esp.rglob('*') if p.is_file()}
for name,row in expected.items():
    p=esp/name;assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
backup=lab/'efi-assets-archive-001';assert not backup.exists();backup.mkdir(mode=0o700)
(backup/'efi-before.json').write_text(json.dumps(before,indent=2))
for name,row in expected.items():
    target=backup/name;target.parent.mkdir(mode=0o700,exist_ok=True)
    with (esp/name).open('rb') as src,target.open('xb') as dst:
        shutil.copyfileobj(src,dst);dst.flush();os.fsync(dst.fileno())
    target.chmod(0o600)
    assert target.stat().st_size==row['bytes'] and sha(target)==row['sha256']
(backup/'manifest.json').write_text(json.dumps(expected,indent=2));os.sync()
guards()
assert {str(p.relative_to(esp)):sha(p) for p in esp.rglob('*') if p.is_file()}==before
for name,row in expected.items():assert sha(backup/name)==row['sha256']
for name in expected:(esp/name).unlink()
for directory in ['harmony-native-diag-004']:(esp/directory).rmdir()
os.sync()
after={str(p.relative_to(esp)):sha(p) for p in esp.rglob('*') if p.is_file()}
assert before.keys()-after.keys()==expected.keys() and not after.keys()-before.keys()
assert all(after[name]==before[name] for name in after)
assert configs()==audit['configs'] and command(['efibootmgr','-v'])==audit['efi']
result=dict(archive=str(backup),archived_files=expected,removed_efi_files=sorted(expected),
    all_other_efi_files_verified_unchanged=len(after),free_after=shutil.disk_usage(esp).free,
    ubuntu_default_unchanged=True,boot_configurations_unchanged=True,reboot_requested=False,
    latest_working_diagnostics_retained=True,experiment_bytes_preserved_in_archive=True)
(backup/'result.json').write_text(json.dumps(result,indent=2));os.sync()
print(json.dumps(result))
'''
compile(payload,'archive-old-diagnostic-assets','exec')
if __name__=='__main__':
    r=subprocess.run(['ssh','-o','ConnectTimeout=3','matebook','sudo -n python3 -'],input=payload,text=True,capture_output=True,timeout=180)
    (out.with_suffix('.stdout')).write_text(r.stdout,encoding='utf-8')
    (out.with_suffix('.stderr')).write_text(r.stderr,encoding='utf-8')
    assert r.returncode==0,r.stderr
    result=json.loads(r.stdout);out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
