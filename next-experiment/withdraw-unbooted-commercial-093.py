"""Archive only our unbooted 093 entry/unique overlay, never shared payloads."""
from pathlib import Path
import json
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
if __name__ == '__main__':
    old = ROOT/'reports/commercial61-native-093'
    new = ROOT/'reports/commercial61-native-094'
    assert not (old/'boot-attempt.json').exists()
    assert not (new/'installation-result.json').exists()
    assert all(json.loads((new/'admission-test.json').read_text()).values())
    expected = json.loads((old/'installation-result.json').read_text())
    expected['ubuntu_boot_id'] = json.loads((ROOT/'reports/commercial61-native-092/post-return-verification.json').read_text())['boot_id']
    code = 'expected='+repr(expected)+'\n'+r'''
from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess
esp=Path('/boot/efi');entries=esp/'loader/entries'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
default='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
status=subprocess.check_output(['bootctl','status','--no-pager'],text=True)
assert ('Default Entry: '+default) in status and ('Current Entry: '+default) in status and 'OneShot Entry:' not in status
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==expected['ubuntu_boot_id']
for action,wanted in [('is-enabled','enabled'),('is-active','active')]:
 assert subprocess.check_output(['systemctl',action,'harmony-lab-screen-off-001.timer'],text=True).strip()==wanted
entry=entries/'commercial61-native-093.conf';payload=esp/'commercial61-native-092/early093.img'
assert entry.read_text()==expected['entry_text']
assert sha(payload)==expected['initrd_sha256']
assert payload.resolve().parent==esp.resolve()/'commercial61-native-092'
assert not payload.is_symlink() and not entry.is_symlink()
assert {p.name for p in entries.glob('commercial61-native-*.conf')}=={'commercial61-native-092.conf','commercial61-native-093.conf'}
for p in entries.glob('*.conf'):
 if p!=entry:
  assert '/commercial61-native-092/early093.img' not in p.read_text()
before={str(p.relative_to(esp)):sha(p) for p in esp.rglob('*') if p.is_file()}
firmware=subprocess.check_output(['efibootmgr','-v'],text=True)
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
archive=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab')/('unbooted-commercial-093-withdrawal-'+stamp)
archive.mkdir(mode=0o700)
records=[]
for p in (entry,payload):
 destination=archive/p.name
 with destination.open('xb') as stream:
  stream.write(p.read_bytes());stream.flush();os.fsync(stream.fileno())
 assert sha(destination)==sha(p)
 records.append(dict(path=str(p.relative_to(esp)),sha256=sha(p),bytes=p.stat().st_size,archived=str(destination)))
result=dict(stamp=stamp,archive=str(archive),removed=records,originally_created_by_agent=True,
 reason='unbooted candidate privacy CLI-format correction',shared_dependencies_removed=False,boot_requested=False)
with (archive/'before.json').open('x') as stream:
 json.dump(result,stream,indent=2);stream.flush();os.fsync(stream.fileno())
for p in (entry,payload):
 assert sha(p)==next(record['sha256'] for record in records if record['path']==str(p.relative_to(esp)))
 p.unlink()
os.sync()
removed={record['path'] for record in records}
assert all((esp/name).is_file() and sha(esp/name)==value for name,value in before.items() if name not in removed)
assert subprocess.check_output(['efibootmgr','-v'],text=True)==firmware
result.update(other_efi_files_unchanged=len(before)-len(removed),firmware_unchanged=True,
 ubuntu_default_unchanged=True,free_bytes=shutil.disk_usage(esp).free)
(archive/'result.json').open('x').write(json.dumps(result,indent=2))
print(json.dumps(result))
'''
    workflow = runpy.run_path(str(BASE/'commercial-workflow-094.py'))
    workflow['configure_local_transport']()
    process = subprocess.run(['ssh', 'matebook', 'sudo -n python3 -'], input=code, text=True,
        capture_output=True, timeout=120)
    assert process.returncode == 0, process.stderr
    result = json.loads(process.stdout)
    (old/'unbooted-withdrawal.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
