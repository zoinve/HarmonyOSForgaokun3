"""Fresh baseline after consumed-entry cleanup; do not reuse old EFI snapshots."""
from pathlib import Path
import json
import subprocess

base=Path(__file__).resolve().parent.parent
out=base/'reports/baremetal-boot-entry-preflight-005.json'
old=json.loads((base/'reports/baremetal-boot-entry-preflight-001.json').read_text())
payload='old='+repr(old['loader_files'])+'\n'+r'''
from pathlib import Path
import subprocess,json,os
def run(args):
 r=subprocess.run(args,capture_output=True,text=True,timeout=30);assert r.returncode==0,r.stderr
 return dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)
assert os.uname().release=='7.1.0-rc3-gaokun3+'
assert 'harmony.diag=1' not in Path('/proc/cmdline').read_text().split()
esp=Path('/boot/efi');current={str(p):p.read_text() for p in (esp/'loader').rglob('*.conf')}
assert current==old,'Original unrelated loader configuration changed; inspect before proceeding'
assert not list((esp/'loader/entries').glob('harmony-native-diag-*'))
guid='4a67b082-0a4c-41cf-b6c7-440b29bb8c4f';variables=Path('/sys/firmware/efi/efivars')
one=variables/('LoaderEntryOneShot-'+guid);assert not one.exists() or not one.read_bytes()[4:].decode('utf-16-le').rstrip('\0')
assert (variables/('LoaderEntryDefault-'+guid)).read_bytes()[4:].decode('utf-16-le').rstrip('\0')=='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
assert run(['systemctl','is-enabled','harmony-lab-screen-off-001.timer'])['stdout'].strip()=='enabled'
assert run(['systemctl','is-active','harmony-lab-screen-off-001.timer'])['stdout'].strip()=='active'
print(json.dumps(dict(boot=run(['bootctl','status','--no-pager']),efi=run(['efibootmgr','-v']),loader_files=current,boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),running_kernel=os.uname().release,screen_off_timer_active=True,post_cleanup_baseline=True,old_diagnostic_entries_absent=True)))
'''
if __name__=='__main__':
    assert not out.exists()
    r=subprocess.run(['ssh','-o','ConnectTimeout=3','matebook','sudo -n python3 -'],input=payload,text=True,capture_output=True,timeout=90);assert r.returncode==0,r.stderr
    d=json.loads(r.stdout);assert d['efi']['stdout']==old['efi']['stdout'];out.write_text(json.dumps(d,indent=2)+'\n')
    print(json.dumps(dict(loader_files=len(d['loader_files']),post_cleanup_baseline=True,screen_off_timer_active=True,boot_id=d['boot_id'])))
