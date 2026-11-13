"""Request the authorized single diagnostic reboot, with final integrity guards."""
from pathlib import Path
import json
import subprocess

base = Path(__file__).resolve().parent.parent
selected = json.loads((base / 'reports/baremetal-diagnostic-one-shot-001.json').read_text())
assert selected['one_shot_verified'] and not selected['reboot_requested']
report = base / 'reports/baremetal-diagnostic-trial-001-start.json'
assert not report.exists()
payload = r'''
from pathlib import Path
import hashlib,json,subprocess,os,time
def sha(p):
    with p.open('rb') as stream: return hashlib.file_digest(stream,'sha256').hexdigest()
def run(args): return subprocess.run(args,capture_output=True,text=True,timeout=30)
lab=Path('/mnt/harmony-lab/work')
assert run(['findmnt','-n','-o','SOURCE,UUID','--target',str(lab)]).stdout.split()==['/dev/nvme0n1p4','00029cdd-1748-4d2f-b73b-8e8164922098']
backup=lab/'boot-entry-install-001'
installed=json.loads((backup/'installation-result.json').read_text())
assert Path(installed['entry']).read_text()==installed['entry_text']
for row in installed['artifacts']: assert sha(Path(row['path']))==row['sha256']
esp=Path('/boot/efi')
for rel,digest in json.loads((backup/'efi-files-before.json').read_text()).items(): assert sha(esp/rel)==digest,rel
guid='4a67b082-0a4c-41cf-b6c7-440b29bb8c4f'
var=Path('/sys/firmware/efi/efivars')
assert (var/('LoaderEntryOneShot-'+guid)).read_bytes()[4:].decode('utf-16-le').rstrip('\0')=='harmony-native-diag-004.conf'
entries=run(['bootctl','list','--json=short','--no-pager']);assert entries.returncode==0
entries=json.loads(entries.stdout)
assert next(e for e in entries if e['isDefault'])['id']=='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
trial=lab/'native-trial-001';assert not trial.exists();trial.mkdir(mode=0o700)
result=dict(before_boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
            before_kernel=os.uname().release,before_cmdline=Path('/proc/cmdline').read_text().strip(),
            diagnostic_entry='harmony-native-diag-004.conf',time_unix=time.time(),
            reboot_requested=True,native_diagnostic_success_not_yet_verified=True,
            harmony_boot_attempted=False)
(trial/'before-reboot.json').write_text(json.dumps(result,indent=2));os.sync()
# Respect session inhibitors; never force a restart or kill applications.
r=run(['systemctl','--check-inhibitors=yes','--no-block','reboot'])
result.update(reboot_command_returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)
(trial/'reboot-command.json').write_text(json.dumps(result,indent=2));os.sync()
print(json.dumps(result,indent=2),flush=True)
'''
compile(payload, 'trial-start-remote', 'exec')
if __name__ == '__main__':
    r = subprocess.run(['ssh', 'matebook', 'sudo -n python3 -'], input=payload,
                       text=True, capture_output=True, timeout=120)
    (base / 'reports/baremetal-diagnostic-trial-001-start.stdout').write_text(r.stdout, encoding='utf-8')
    (base / 'reports/baremetal-diagnostic-trial-001-start.stderr').write_text(r.stderr, encoding='utf-8')
    if r.stdout.strip():
        result = json.loads(r.stdout)
        report.write_text(json.dumps(result, indent=2), encoding='utf-8')
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(dict(ssh_returncode=r.returncode,stderr=r.stderr,
                              reboot_outcome_unknown=True),indent=2))
