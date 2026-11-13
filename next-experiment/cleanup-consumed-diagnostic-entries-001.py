"""Archive and remove only our four verified consumed diagnostic entry configs."""
from pathlib import Path
import hashlib
import json
import subprocess

base = Path(__file__).resolve().parent.parent
reports = base / 'reports'
report = reports / 'boot-entry-cleanup-001.json'
backup = reports / 'boot-entry-cleanup-001-backup'
assert not report.exists() and not backup.exists()
collection_dir = reports / 'baremetal-native-trial-004-collected'
collection = json.loads((collection_dir / 'collection.json').read_text())
assert collection['boot_id_changed'] and collection['running_kernel'] == '7.1.0-rc3-gaokun3+'
assert len(collection['files']) == 116
for row in collection['files']:
    data = (collection_dir / row['path']).read_bytes()
    assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256']
expected = {}
for trial, candidate in (('001', '004'), ('002', '005'), ('003', '006'), ('004', '007')):
    installed = json.loads((reports / ('baremetal-boot-entry-installed-' + trial + '.json')).read_text())
    assert Path(installed['entry']).name == 'harmony-native-diag-' + candidate + '+1.conf'
    name = 'harmony-native-diag-' + candidate + '+0-1.conf'
    expected[name] = installed['entry_text'].encode()
# These exact expected config bytes are archived locally before any remote removal.
backup.mkdir()
for name, data in expected.items():
    with (backup / name).open('xb') as stream:
        stream.write(data)
    assert (backup / name).read_bytes() == data

payload = 'expected=' + repr(expected) + '\nexpected_boot=' + repr(collection['after_boot_id']) + '\n' + r'''
from pathlib import Path
import hashlib,json,os,stat,subprocess
def run(args):
    r=subprocess.run(args,capture_output=True,text=True,timeout=30)
    assert r.returncode==0,r.stderr
    return r.stdout
def digest(p):
    with p.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==expected_boot
assert os.uname().release=='7.1.0-rc3-gaokun3+'
assert 'harmony.diag=1' not in Path('/proc/cmdline').read_text().split()
esp=Path('/boot/efi');entries=esp/'loader/entries'
assert run(['findmnt','-n','-o','SOURCE','--mountpoint',str(esp)]).strip()=='/dev/nvme0n1p1'
guid='4a67b082-0a4c-41cf-b6c7-440b29bb8c4f';var=Path('/sys/firmware/efi/efivars')
default=var/('LoaderEntryDefault-'+guid);one=var/('LoaderEntryOneShot-'+guid)
saved_default=default.read_bytes()
assert saved_default[4:].decode('utf-16-le').rstrip('\0')=='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
assert not one.exists() or not one.read_bytes()[4:].decode('utf-16-le').rstrip('\0')
efi_before=run(['efibootmgr','-v'])
before={str(p.relative_to(esp)):digest(p) for p in esp.rglob('*') if p.is_file()}
assert set(expected)=={'harmony-native-diag-'+v+'+0-1.conf' for v in ('004','005','006','007')}
for name,data in expected.items():
    p=entries/name
    assert stat.S_ISREG(p.lstat().st_mode) and p.read_bytes()==data,name
archive=Path('/var/lib/harmony-lab-boot-entry-cleanup-001');assert not archive.exists()
archive.mkdir(mode=0o700)
for name,data in expected.items():
    with (archive/name).open('xb') as stream:stream.write(data);stream.flush();os.fsync(stream.fileno())
    assert (archive/name).read_bytes()==data
(archive/'efi-files-before.json').write_text(json.dumps(before,indent=2))
os.sync()
# Recheck all targets and both boot-selection guards before the first unlink.
assert default.read_bytes()==saved_default
assert not one.exists() or not one.read_bytes()[4:].decode('utf-16-le').rstrip('\0')
for name,data in expected.items():assert (entries/name).read_bytes()==data and (archive/name).read_bytes()==data
for name in expected:(entries/name).unlink()
os.sync()
after={str(p.relative_to(esp)):digest(p) for p in esp.rglob('*') if p.is_file()}
removed={'loader/entries/'+name for name in expected}
assert set(before)-set(after)==removed and not set(after)-set(before)
assert all(digest==after[name] for name,digest in before.items() if name not in removed)
assert default.read_bytes()==saved_default and run(['efibootmgr','-v'])==efi_before
assert not one.exists() or not one.read_bytes()[4:].decode('utf-16-le').rstrip('\0')
result=dict(removed_entry_files=sorted(removed),archive_directory=str(archive),
    archived_sha256={name:digest(archive/name) for name in expected},
    other_efi_files_verified_unchanged=len(after),ubuntu_default_unchanged=True,
    firmware_boot_entries_unchanged=True,boot_id=expected_boot,reboot_requested=False,
    diagnostic_assets_removed=False,raw_logs_removed=False,boot_list=run(['bootctl','list','--no-pager']))
(archive/'result.json').write_text(json.dumps(result,indent=2));os.sync()
print(json.dumps(result))
'''

if __name__ == '__main__':
    compile(payload, 'cleanup-consumed-entries-remote', 'exec')
    result = subprocess.run(['ssh', '-o', 'ConnectTimeout=3', 'matebook', 'sudo -n python3 -'],
                            input=payload, capture_output=True, text=True, timeout=120)
    (backup / 'operation.stdout').write_text(result.stdout, encoding='utf-8')
    (backup / 'operation.stderr').write_text(result.stderr, encoding='utf-8')
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    for name, content in expected.items():
        assert data['archived_sha256'][name] == hashlib.sha256(content).hexdigest()
    report.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in data.items() if key != 'boot_list'}, indent=2))
