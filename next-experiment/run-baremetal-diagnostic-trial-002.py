"""Single 005 diagnostic trial; immediately observe SSH, then collect verified raw logs."""
from pathlib import Path
import json
import runpy
import subprocess

base = Path(__file__).resolve().parent.parent
reports = base / 'reports'
out = reports / 'baremetal-native-trial-002-evidence'

prepare = r'''
from pathlib import Path
import os,json,subprocess,hashlib
def run(args):
    r=subprocess.run(args,capture_output=True,text=True,timeout=30)
    assert r.returncode==0,r.stderr
    return r.stdout
def sha(p):
    with p.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
lab=Path('/mnt/harmony-lab/work');esp=Path('/boot/efi')
assert run(['findmnt','-n','-o','SOURCE,UUID','--target',str(lab)]).split()==['/dev/nvme0n1p4','00029cdd-1748-4d2f-b73b-8e8164922098']
assert 'harmony.diag=1' not in Path('/proc/cmdline').read_text().split()
backup=lab/'boot-entry-install-002'
installed=json.loads((backup/'installation-result.json').read_text())
assert Path(installed['entry']).read_text()==installed['entry_text']
for row in installed['artifacts']:assert sha(Path(row['path']))==row['sha256']
for rel,digest in json.loads((backup/'efi-files-before.json').read_text()).items():assert sha(esp/rel)==digest,rel
guid='4a67b082-0a4c-41cf-b6c7-440b29bb8c4f';var=Path('/sys/firmware/efi/efivars')
default=var/('LoaderEntryDefault-'+guid);one=var/('LoaderEntryOneShot-'+guid)
saved_default=default.read_bytes()
assert saved_default[4:].decode('utf-16-le').rstrip('\0')=='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
assert not one.exists() or not one.read_bytes()[4:].decode('utf-16-le').rstrip('\0')
entries=json.loads(run(['bootctl','list','--json=short','--no-pager']))
entry=next(e for e in entries if e['id']=='harmony-native-diag-005.conf')
assert entry['triesLeft']==1
trial=lab/'native-trial-002';assert not trial.exists();trial.mkdir(mode=0o700)
before=dict(before_boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
    before_kernel=os.uname().release,before_cmdline=Path('/proc/cmdline').read_text().strip(),
    diagnostic_entry=entry['id'],harmony_boot_attempted=False,
    prior_log_directories=sorted(p.name for p in lab.parent.glob('native-diag-001-*')))
(trial/'before-reboot.json').write_text(json.dumps(before,indent=2));os.sync()
run(['bootctl','set-oneshot',entry['id']])
assert one.read_bytes()[4:].decode('utf-16-le').rstrip('\0')==entry['id']
assert default.read_bytes()==saved_default
for rel,digest in json.loads((backup/'efi-files-before.json').read_text()).items():assert sha(esp/rel)==digest,rel
before['one_shot_verified']=True
(trial/'selection.json').write_text(json.dumps(before,indent=2));os.sync()
print(json.dumps(before),flush=True)
'''

reboot = r'''
from pathlib import Path
import os,json,subprocess,hashlib
trial=Path('/mnt/harmony-lab/work/native-trial-002')
before=json.loads((trial/'selection.json').read_text())
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==before['before_boot_id']
guid='4a67b082-0a4c-41cf-b6c7-440b29bb8c4f';var=Path('/sys/firmware/efi/efivars')
assert (var/('LoaderEntryOneShot-'+guid)).read_bytes()[4:].decode('utf-16-le').rstrip('\0')==before['diagnostic_entry']
assert (var/('LoaderEntryDefault-'+guid)).read_bytes()[4:].decode('utf-16-le').rstrip('\0')=='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
installed=json.loads((trial.parent/'boot-entry-install-002/installation-result.json').read_text())
assert Path(installed['entry']).read_text()==installed['entry_text']
for row in installed['artifacts']:
    with Path(row['path']).open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==row['sha256']
assert not (trial/'reboot-requested.json').exists()
(trial/'reboot-requested.json').write_text(json.dumps(dict(autonomous_reboot_authorized=True,
    session_inhibitor_override_authorized=True,hard_reset=False)))
os.sync()
r=subprocess.run(['systemctl','--ignore-inhibitors','--no-block','reboot'],capture_output=True,text=True,timeout=20)
print(json.dumps(dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)),flush=True)
raise SystemExit(r.returncode)
'''

probe_code = "import json,os;from pathlib import Path;print(json.dumps(dict(boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),kernel=os.uname().release,cmdline=Path('/proc/cmdline').read_text().strip())))"


def ssh_payload(payload, timeout=120):
    return subprocess.run(['ssh', '-o', 'ConnectTimeout=3', '-o', 'ConnectionAttempts=1',
                           'matebook', 'sudo -n python3 -'], input=payload,
                          text=True, capture_output=True, timeout=timeout)


def probe():
    try:
        result = ssh_payload(probe_code, timeout=8)
    except subprocess.TimeoutExpired:
        return None
    if 'REMOTE HOST IDENTIFICATION HAS CHANGED' in result.stderr or 'Host key verification failed' in result.stderr:
        raise RuntimeError('SSH host-key verification failed; refusing to bypass it')
    if result.returncode:
        return None
    try:
        return json.loads(result.stdout)
    except ValueError:
        return None


for code in (prepare, reboot, probe_code):
    compile(code, 'trial-002-remote', 'exec')

if __name__ == '__main__':
    assert not out.exists()
    assert (reports / 'baremetal-boot-entry-installed-002.json').is_file()
    out.mkdir()
    result = ssh_payload(prepare)
    (out / 'prepare.stdout').write_text(result.stdout, encoding='utf-8')
    (out / 'prepare.stderr').write_text(result.stderr, encoding='utf-8')
    result.check_returncode()
    before = json.loads(result.stdout)
    try:
        result = ssh_payload(reboot, timeout=30)
    except subprocess.TimeoutExpired as error:
        result = subprocess.CompletedProcess('ssh', 255, '', 'SSH interrupted or timed out during reboot request')
    (out / 'reboot-command.json').write_text(json.dumps(dict(ssh_returncode=result.returncode,
        stdout=result.stdout,stderr=result.stderr),indent=2), encoding='utf-8')
    assert result.returncode in (0, 255), 'Reboot request refused; no automatic override or repeat request'
    # Start observing immediately, including when shutdown interrupted SSH.
    wait = runpy.run_path(str(base / 'next-experiment/baremetal-reconnect-002.py'))['wait_for_return']
    observation = wait(before['before_boot_id'], probe, timeout=600, interval=1)
    (out / 'reconnect.json').write_text(json.dumps(observation,indent=2), encoding='utf-8')
    assert observation['returned'], 'SSH did not return with a changed boot ID; no automatic repeat reboot'
    assert observation['returned']['kernel']=='7.1.0-rc3-gaokun3+', 'Unexpected returned kernel; inspect before collection'
    source = (base / 'next-experiment/collect-baremetal-diagnostic-trial-001.py').read_text()
    source = source.replace("out = base / 'reports/baremetal-native-trial-001-evidence'",
                            "out = base / 'reports/baremetal-native-trial-002-collected'")
    source = source.replace('work/native-trial-001/', 'work/native-trial-002/')
    source = source.replace('work/boot-entry-install-001', 'work/boot-entry-install-002')
    source = source.replace("glob('harmony-native-diag-004*')", "glob('harmony-native-diag-005*')")
    assert source.count('time.sleep(300)')==1
    source = source.replace('time.sleep(300)', 'pass  # SSH has just returned; collect without a fixed delay')
    exec(compile(source, 'collector-trial-002', 'exec'), {'__file__': __file__, '__name__': '__main__'})
