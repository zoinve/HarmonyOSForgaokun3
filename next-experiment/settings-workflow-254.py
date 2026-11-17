"""Install/boot253 directly; omit repeated filesystem and historical test suites."""
from pathlib import Path
import base64
import datetime
import hashlib
import json
import runpy
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/commercial61-native-253'
SSH = runpy.run_path(str(ROOT / 'next-experiment/deploy-settings-data-198.py'))['SSH']
GUARD = r'''
from pathlib import Path
import hashlib,json,os,stat,subprocess
os.environ['LC_ALL']='C';os.umask(0o077)
def command(args):return subprocess.check_output(args,text=True,stderr=subprocess.PIPE,timeout=30)
assert os.geteuid()==0
default='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
status=command(['bootctl','status','--no-pager'])
assert 'Current Entry: '+default in status and 'Default Entry: '+default in status and 'OneShot Entry:' not in status
for action,want in [('is-enabled','enabled'),('is-active','active')]:
 assert subprocess.run(['systemctl',action,'harmony-lab-screen-off-001.timer'],capture_output=True,text=True).stdout.strip()==want
assert command(['blkid','-p','-s','UUID','-o','value','/dev/nvme0n1p4']).strip()=='00029cdd-1748-4d2f-b73b-8e8164922098'
assert not subprocess.run(['findmnt','-rn','-S','/dev/nvme0n1p4'],capture_output=True,text=True).stdout.strip()
memory={line.split(':')[0]:int(line.split()[1])*1024 for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith(('MemTotal:','MemAvailable:'))}
assert memory['MemTotal']>=15*1024**3 and memory['MemAvailable']>=11*1024**3
'''
INSTALL = r'''
import base64,shutil
esp=Path('/boot/efi');entries=esp/'loader/entries'
work=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/commercial61-native-253')
entry=entries/'commercial61-native-253.conf';image=esp/'set253.img'
old_entry=entries/'commercial61-native-235.conf'
assert not work.exists() and not entry.exists() and not image.exists()
assert old_entry.is_file() and (entries/'commercial61-native-173.conf').is_file()
assert (entries/'harmonyos-gpu-manual.conf').is_file()
old=old_entry.read_text()
new='\n'.join('title native Settings real-time budget 253 - AUTO RETURN 900 SEC' if line.startswith('title ') else line.replace('set235.img','set253.img') for line in old.splitlines())+'\n'
assert 'set253.img' in new and 'set235.img' not in new
decoded={name:base64.b64decode(row['base64']) for name,row in payload.items()}
for name,data in decoded.items():assert hashlib.sha256(data).hexdigest()==payload[name]['sha256']
assert hashlib.sha256(decoded['bootstrap-runtime087']).hexdigest()=='fe80eef0831fda293ff0bbebb66f9c2d0c6c8c6b739b47cc8714653479ea7122'
assert shutil.disk_usage(esp).free>len(decoded['initrd.img'])+32*1024**2+65536
firmware=command(['efibootmgr','-v'])
work.mkdir(mode=0o700)
def write(path,data,mode):
 with path.open('xb') as stream:
  stream.write(data);stream.flush();os.fsync(stream.fileno())
 if path.is_relative_to(work):path.chmod(mode)
for name,data in decoded.items():write(work/name,data,0o600 if name=='initrd.img' else 0o755)
write(image,decoded['initrd.img'],0o600)
write(entry,new.encode(),0o600)
archive=dict(name=old_entry.name,sha256=hashlib.sha256(old.encode()).hexdigest(),content=old,
 user_authorized_retention=True,kept_experiments=['commercial61-native-173.conf','commercial61-native-253.conf'])
write(work/'retired-entry-235.json',json.dumps(archive,indent=2).encode(),0o600)
assert old_entry.read_text()==old
old_entry.unlink()
assert command(['efibootmgr','-v'])==firmware
subprocess.run(['sync','-f',str(esp)],check=True,timeout=30)
result=dict(installed=True,entry=entry.name,initrd_sha256=payload['initrd.img']['sha256'],
 desktop173_retained=True,prior235_entry_archived_removed=True,shared_payloads_deleted=False,
 original_images_written=False,active165_written=False,settings_candidate_written=False,
 filesystem_hash_and_tree_suites_skipped_at_user_request=True,
 prior249_tree_equality_failure_not_reclassified=True,firmware_unchanged=True,
 ubuntu_default_preserved=True,screenoff_timer_enabled_active=True,boot_requested=False)
write(work/'installation-result.json',json.dumps(result,indent=2).encode(),0o600)
print(json.dumps(result,indent=2))
'''


def remote(source, timeout=180):
    proc = subprocess.run(SSH + ['sudo -n python3 -'], input=source, text=True,
                          capture_output=True, timeout=timeout)
    assert proc.returncode == 0, proc.stderr
    return proc.stdout


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ['install', 'boot']
    if sys.argv[1] == 'install':
        assert not (REPORT / 'installation-result.json').exists()
        metadata = json.loads((REPORT / 'result.json').read_text())
        rows = {row['name']:row for row in metadata['artifacts']}
        payload = {}
        for name in ['init', 'bootstrap', 'bootstrap-runtime087', 'initrd.img']:
            source = 'minimal-overlay.img' if name == 'initrd.img' else name
            data = subprocess.check_output(['wsl', '-d', 'Debian', '--', 'cat',
                '/home/zoinve/harmony-virgl-883/commercial61-native-253/' + source])
            expected = json.loads((REPORT / 'overlay-result.json').read_text())['sha256'] if name == 'initrd.img' else rows[name]['sha256']
            assert hashlib.sha256(data).hexdigest() == expected
            payload[name] = dict(base64=base64.b64encode(data).decode(), sha256=expected)
        text = remote('payload=' + repr(payload) + '\n' + GUARD + INSTALL)
        (REPORT / 'installation-result.json').open('x').write(text)
        print(text)
    else:
        assert (REPORT / 'installation-result.json').is_file()
        record = REPORT / 'boot-attempt.json'
        assert not record.exists(), 'single attempt only'
        state = json.loads(remote(GUARD + "\nprint(json.dumps(dict(boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip())))"))
        record.open('x').write(json.dumps(dict(start_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            before_boot_id=state['boot_id'], entry='commercial61-native-253.conf', attempt_count=1,
            user_requested_direct_next_step=True,settings_window_verified=False), indent=2))
        code = "import subprocess;from pathlib import Path;assert Path('/boot/efi/loader/entries/commercial61-native-253.conf').is_file();subprocess.run(['bootctl','set-oneshot','commercial61-native-253.conf'],check=True);subprocess.run(['systemctl','reboot'],check=True)"
        proc = subprocess.run(SSH + ['sudo -n python3 -'], input=code, text=True, capture_output=True, timeout=40)
        result = dict(reboot_command_exit=proc.returncode, stdout=proc.stdout, stderr=proc.stderr,
                      returned_to_ubuntu=False, no_retry_requested=True)
        (REPORT / 'boot-command.json').open('x').write(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2))
