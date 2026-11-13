"""Select the verified diagnostic once, without changing defaults or rebooting."""
from pathlib import Path
import json
import subprocess

base = Path(__file__).resolve().parent.parent
installed = json.loads((base / 'reports/baremetal-boot-entry-installed-001.json').read_text())
assert installed['ubuntu_default_unchanged'] and not installed['reboot_requested']
report = base / 'reports/baremetal-diagnostic-one-shot-001.json'
assert not report.exists()
payload = 'installed = ' + repr(installed) + '\n' + r'''
from pathlib import Path
import hashlib,json,subprocess,os
def sha(p):
    with p.open('rb') as stream: return hashlib.file_digest(stream,'sha256').hexdigest()
def run(args): return subprocess.run(args,capture_output=True,text=True,timeout=30)
esp=Path('/boot/efi')
backup=Path('/mnt/harmony-lab/work/boot-entry-install-001')
assert Path(installed['entry']).read_text()==installed['entry_text']
for row in installed['artifacts']: assert sha(Path(row['path']))==row['sha256']
before=json.loads((backup/'efi-files-before.json').read_text())
for rel,digest in before.items(): assert sha(esp/rel)==digest,rel
guid='4a67b082-0a4c-41cf-b6c7-440b29bb8c4f'
variables=Path('/sys/firmware/efi/efivars')
one=variables/('LoaderEntryOneShot-'+guid)
default=variables/('LoaderEntryDefault-'+guid)
assert not one.exists(),'Refuse to replace an existing one-shot selection'
default_bytes=default.read_bytes()
firmware_before=run(['efibootmgr','-v']);assert firmware_before.returncode==0
entries=json.loads(run(['bootctl','list','--json=short','--no-pager']).stdout)
entry=next(r for r in entries if r['id']=='harmony-native-diag-004.conf')
assert entry['triesLeft']==1 and not entry['isDefault']
assert next(r for r in entries if r['isDefault'])['id']=='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
r=run(['bootctl','set-oneshot',entry['id']])
value=one.read_bytes()[4:].decode('utf-16-le').rstrip('\0') if one.exists() else None
verified=r.returncode==0 and value==entry['id']
assert default.read_bytes()==default_bytes
for rel,digest in before.items(): assert sha(esp/rel)==digest,rel
after=run(['efibootmgr','-v'])
assert after.returncode==0 and after.stdout==firmware_before.stdout
result=dict(command_returncode=r.returncode,stdout=r.stdout,stderr=r.stderr,one_shot_value=value,
            one_shot_verified=verified,default_variable_unchanged=True,existing_efi_files_unchanged=True,
            firmware_boot_entries_unchanged=True,reboot_requested=False,native_boot_attempted=False)
(backup/'one-shot-result.json').write_text(json.dumps(result,indent=2));os.sync()
print(json.dumps(result,indent=2))
'''
compile(payload, 'select-once-remote', 'exec')
if __name__ == '__main__':
    r = subprocess.run(['ssh', 'matebook', 'sudo -n python3 -'], input=payload,
                       text=True, capture_output=True, timeout=120)
    (base / 'reports/baremetal-diagnostic-one-shot-001.stderr').write_text(r.stderr, encoding='utf-8')
    r.check_returncode()
    result = json.loads(r.stdout)
    report.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
