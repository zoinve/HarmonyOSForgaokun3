"""One guarded diagnostic boot, immediate bounded observation, never reboot twice."""
from pathlib import Path
import datetime
import hashlib
import json
import runpy
import subprocess
import time
import uuid

BASE = Path(__file__).resolve().parents[1]
STAGE = '/home/zoinve/.local/share/harmony-arm64-kvm-lab/native-original-graphics-boot-043'
head = runpy.run_path(str(Path(__file__).with_name('archive-native-consumed-022-for-043.py')))['REMOTE']
head = head.split('\nguards()\nassert set(request')[0]
PREPARE = head + r'''
root=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/native-original-graphics-boot-043')
prepared=root/'boot-prepared.json'
guards()
assert rows()==request['inventory']['files'] and configs()==request['inventory']['configs']
assert shutil.disk_usage(esp).free>64*1024*1024
assert not prepared.exists() and not (root/'reboot-requested.json').exists()
assert sha(root/'result.json')==request['candidate_manifest_sha256']
for row in request['artifacts']:
 p=root/row['name']
 assert p.parent==root and p.is_file() and not p.is_symlink()
 assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256']
entry=Path(request['installation']['entry'])
assert entry==esp/'loader/entries/native-original-graphics-043+1.conf'
assert sha(entry)==request['installation']['entry_sha256']
assert entry.read_text()==request['installation']['entry_text']
listing=json.loads(cmd(['bootctl','list','--json=short']))
selected=[r for r in listing if r.get('id')==request['installation']['entry_id']]
assert len(selected)==1 and selected[0].get('triesLeft')==1
assert subprocess.run(['findmnt','-rn','--source','/dev/nvme0n1p4'],capture_output=True).returncode!=0
result=dict(before_boot_id=request['inventory']['boot_id'],entry_id=request['installation']['entry_id'],
 operation_nonce=request['operation_nonce'],
 efi_files_before=rows(),configs_before=configs(),firmware=cmd(['efibootmgr','-v']),
 target_seconds=240,outer_fallback_seconds=420,hardware_watchdog=False,automatic_input_injection=False)
with prepared.open('x') as f:
 json.dump(result,f,indent=2);f.flush();os.fsync(f.fileno())
fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY)
try: os.fsync(fd)
finally: os.close(fd)
subprocess.run(['bootctl','set-oneshot',request['installation']['entry_id']],check=True,timeout=30)
status=cmd(['bootctl','status','--no-pager'])
assert 'OneShot Entry: '+request['installation']['entry_id'] in status
assert 'Default Entry: 8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf' in status
assert rows()==request['inventory']['files'] and configs()==request['inventory']['configs']
print(json.dumps(result))
'''
REBOOT = head + r'''
root=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/native-original-graphics-boot-043')
prepared=json.loads((root/'boot-prepared.json').read_text())
assert prepared['operation_nonce']==expected_nonce
assert os.getuid()==0 and Path('/proc/sys/kernel/random/boot_id').read_text().strip()==prepared['before_boot_id']
assert cmd(['uname','-r']).strip()=='7.1.0-rc3-gaokun3+'
assert 'harmony.diag=1' not in Path('/proc/cmdline').read_text()
assert cmd(['findmnt','-n','-o','SOURCE,FSTYPE','--target',str(esp)]).split()==['/dev/nvme0n1p1','vfat']
assert cmd(['blkid','-s','PARTUUID','-o','value','/dev/nvme0n1p1']).strip()=='922f37b2-3474-4761-a370-5aa1dcd7c476'
status=cmd(['bootctl','status','--no-pager'])
assert 'OneShot Entry: '+prepared['entry_id'] in status
assert 'Default Entry: 8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf' in status
assert rows()==prepared['efi_files_before'] and configs()==prepared['configs_before']
assert cmd(['efibootmgr','-v'])==prepared['firmware']
assert cmd(['systemctl','is-active','harmony-lab-screen-off-001.timer']).strip()=='active'
request_file=root/'reboot-requested.json'
with request_file.open('x') as f:
 json.dump(dict(before_boot_id=prepared['before_boot_id'],entry_id=prepared['entry_id'],attempt_count=1),f)
 f.flush();os.fsync(f.fileno())
fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY)
try: os.fsync(fd)
finally: os.close(fd)
print('NATIVE043_REBOOT_REQUESTED',flush=True)
subprocess.run(['systemctl','--ignore-inhibitors','--no-block','reboot'],check=True,timeout=30)
'''
CANCEL_OWN_SELECTION = head + r'''
root=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/native-original-graphics-boot-043')
prepared_path=root/'boot-prepared.json'
if not prepared_path.exists():
 print(json.dumps(dict(cancelled=False,reason='no prepared journal')))
else:
 prepared=json.loads(prepared_path.read_text())
 assert prepared['operation_nonce']==request['operation_nonce']
 assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==prepared['before_boot_id']
 assert cmd(['uname','-r']).strip()=='7.1.0-rc3-gaokun3+'
 status=cmd(['bootctl','status','--no-pager'])
 assert 'Default Entry: 8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf' in status
 if 'OneShot Entry:' in status:
  assert 'OneShot Entry: '+prepared['entry_id'] in status
  subprocess.run(['bootctl','set-oneshot',''],check=True,timeout=30)
  assert 'OneShot Entry:' not in cmd(['bootctl','status','--no-pager'])
  print(json.dumps(dict(cancelled=True,only_own_nonce=True)))
 else: print(json.dumps(dict(cancelled=False,reason='no pending selection')))
'''
PROBE = "python3 -c \"import json,os,pathlib; print(json.dumps(dict(boot_id=pathlib.Path('/proc/sys/kernel/random/boot_id').read_text().strip(),release=os.uname().release,cmdline=pathlib.Path('/proc/cmdline').read_text().strip())))\""


def observe_return(before, *, probe, clock=time.monotonic, delay=time.sleep, timeout=720):
    start = clock()
    attempts = []
    while clock() - start < timeout:
        row = dict(attempt=len(attempts) + 1, elapsed_seconds=clock() - start)
        try:
            reply = probe()  # Deliberately before any delay.
            row.update(returncode=reply.returncode, stderr=reply.stderr[-1024:])
            if any(text in reply.stderr.lower() for text in
                   ('host key verification failed', 'remote host identification has changed', 'permission denied')):
                raise RuntimeError('SSH identity/authentication failure; no verification bypass or reboot retry')
            if reply.returncode == 0:
                identity = json.loads(reply.stdout)
                row.update(boot_id=identity['boot_id'], release=identity['release'])
                attempts.append(row)
                if (identity['boot_id'] != before and identity['release'] == '7.1.0-rc3-gaokun3+'
                        and 'harmony.diag=1' not in identity['cmdline']):
                    return dict(returned=True, before_boot_id=before, after_boot_id=identity['boot_id'],
                                identity=identity, attempts=attempts, elapsed_seconds=clock() - start)
            else:
                attempts.append(row)
        except subprocess.TimeoutExpired:
            attempts.append(dict(row, timeout=True))
        except (json.JSONDecodeError, KeyError, TypeError) as error:
            attempts.append(dict(row, invalid_response=str(error)))
        delay(min(1, max(0, timeout - (clock() - start))))
    return dict(returned=False, before_boot_id=before, attempts=attempts, elapsed_seconds=clock() - start)


def write_json(path, value):
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2)


if __name__ == '__main__':
    out = BASE/'reports/native-original-graphics-boot-043'
    assert not (out/'boot-preflight.json').exists() and not (out/'boot-observation.json').exists()
    installed = json.loads((BASE/'reports/native-presentation-043-installation.json').read_text())
    assert installed['target_budget_seconds'] == 240 and installed['outer_fallback_seconds'] == 420
    assert not installed['reboot_requested'] and not installed['automatic_input_injection']
    candidate_path = out/'result.json'
    candidate = json.loads(candidate_path.read_text())
    request = dict(installation=installed, artifacts=candidate['artifacts'],
                   operation_nonce=str(uuid.uuid4()),
                   candidate_manifest_sha256=hashlib.sha256(candidate_path.read_bytes()).hexdigest(),
                   inventory=dict(boot_id=installed['boot_id'], files=installed['efi_files_after'],
                                  configs=installed['configs_after'], firmware=installed['firmware']))
    prepared = subprocess.run(['ssh', 'matebook', 'sudo -n python3 -'],
                              input='request='+repr(request)+'\n'+PREPARE,
                              text=True, capture_output=True, timeout=180)
    if prepared.returncode:
        cancelled = subprocess.run(['ssh', 'matebook', 'sudo -n python3 -'],
                                  input='request='+repr(request)+'\n'+CANCEL_OWN_SELECTION,
                                  text=True, capture_output=True, timeout=60)
        write_json(out/'preparation-failure.json', dict(stderr=prepared.stderr,
                   cancellation_returncode=cancelled.returncode, cancellation_stdout=cancelled.stdout,
                   cancellation_stderr=cancelled.stderr))
        raise RuntimeError(prepared.stderr)
    preflight = json.loads(prepared.stdout)
    write_json(out/'boot-preflight.json', preflight)
    write_json(out/'boot-attempt.json', dict(before_boot_id=preflight['before_boot_id'], attempt_count=1,
               entry_id=preflight['entry_id'], start_utc=datetime.datetime.now(datetime.timezone.utc).isoformat()))
    try:
        reboot = subprocess.run(['ssh', 'matebook', 'sudo -n python3 -'],
                                input='expected_nonce='+repr(preflight['operation_nonce'])+'\n'+REBOOT,
                                text=True, capture_output=True, timeout=40)
        command = dict(returncode=reboot.returncode, stdout=reboot.stdout, stderr=reboot.stderr)
    except subprocess.TimeoutExpired:
        command = dict(returncode=None, timeout=True)
    write_json(out/'reboot-command.json', command)
    if command['returncode'] not in (0, 255, None):
        cancelled = subprocess.run(['ssh', 'matebook', 'sudo -n python3 -'],
                                  input='request='+repr(request)+'\n'+CANCEL_OWN_SELECTION,
                                  text=True, capture_output=True, timeout=60)
        write_json(out/'cancel-own-selection.json', dict(returncode=cancelled.returncode,
                   stdout=cancelled.stdout,stderr=cancelled.stderr))
        raise RuntimeError('Reboot request refused; no boot retry: '+str(command))
    def probe():
        return subprocess.run(['ssh', '-o', 'ConnectTimeout=3', '-o', 'ConnectionAttempts=1',
                               '-o', 'BatchMode=yes', 'matebook', PROBE],
                              text=True, capture_output=True, timeout=8)
    observation = observe_return(preflight['before_boot_id'], probe=probe)
    write_json(out/'boot-observation.json', observation)
    print(json.dumps(dict(returned=observation['returned'], attempts=len(observation['attempts']),
                          after_boot_id=observation.get('after_boot_id'),
                          elapsed_seconds=observation['elapsed_seconds'])))
    if not observation['returned']:
        raise SystemExit('No Ubuntu return within bounded observation; never automatically reboot again')
