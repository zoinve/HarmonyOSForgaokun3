"""Independently verify collected logs and Ubuntu state without a display setter."""
from pathlib import Path
import hashlib
import json
import subprocess

base=Path(__file__).resolve().parent.parent
out=base/'reports/baremetal-native-trial-005-independent-verification.json'
saved=base/'reports/baremetal-native-trial-005-collected'
observation=json.loads((base/'reports/baremetal-native-trial-005-evidence/reconnect.json').read_text())
manifest=json.loads((saved/'collection.json').read_text())
for row in manifest['files']:
    p=saved/row['path'];assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
payload='expected_boot_id='+repr(observation['returned']['boot_id'])+'\n'+r'''
from pathlib import Path
import hashlib,json,os,runpy,subprocess
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==expected_boot_id
assert os.uname().release=='7.1.0-rc3-gaokun3+'
assert 'harmony.diag=1' not in Path('/proc/cmdline').read_text().split()
def readonly_runner(args,**kwargs):
 assert 'set-property' not in args,'Verifier must not alter display state'
 return subprocess.run(args,**kwargs)
rows=runpy.run_path('/usr/local/libexec/harmony-lab-screen-off-001.py')['run_once'](runner=readonly_runner)
assert rows and all(r['state']=='off' and not r['changed'] for r in rows),rows
def command(args):return subprocess.check_output(args,text=True,timeout=20).strip()
assert command(['systemctl','is-enabled','harmony-lab-screen-off-001.timer'])=='enabled'
assert command(['systemctl','is-active','harmony-lab-screen-off-001.timer'])=='active'
status=command(['systemctl','show','harmony-lab-screen-off-001.service','--property=Result','--property=ExecMainStatus','--property=ExecMainStartTimestamp'])
assert 'Result=success' in status and 'ExecMainStatus=0' in status,status
guid='4a67b082-0a4c-41cf-b6c7-440b29bb8c4f';v=Path('/sys/firmware/efi/efivars')
default=(v/('LoaderEntryDefault-'+guid)).read_bytes()[4:].decode('utf-16-le').rstrip('\0');assert default=='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
one=v/('LoaderEntryOneShot-'+guid);assert not one.exists() or not one.read_bytes()[4:].decode('utf-16-le').rstrip('\0')
entry=Path('/boot/efi/loader/entries/harmony-native-diag-008+0-1.conf');assert entry.is_file()
expected=json.loads(Path('/mnt/harmony-lab/work/boot-entry-install-005/installation-result.json').read_text());assert entry.read_text()==expected['entry_text']
print(json.dumps(dict(boot_id=expected_boot_id,running_kernel=os.uname().release,screen_rows=rows,screen_state_changed_by_verifier=False,physical_screen_observed=False,screen_off_timer_enabled_active=True,screen_service=status,persistent_default=default,one_shot_absent=True,consumed_entry=str(entry),consumed_entry_sha256=hashlib.sha256(entry.read_bytes()).hexdigest())))
'''
if __name__=='__main__':
    assert not out.exists()
    r=subprocess.run(['ssh','-o','ConnectTimeout=3','matebook','sudo -n python3 -'],input=payload,text=True,capture_output=True,timeout=90);assert r.returncode==0,r.stderr
    d=json.loads(r.stdout);d['raw_log_sizes_and_hashes_verified']=len(manifest['files']);out.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
