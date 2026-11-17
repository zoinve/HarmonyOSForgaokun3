"""Archive and remove only unreferenced old Harmony EFI artifacts; retain every menu entry."""
from pathlib import Path
import inspect
import json
import re
import subprocess
import sys


def candidate_paths(files, configs):
    texts = '\n'.join(configs.values()).replace('\\', '/').casefold()
    allowed = {'initrd.img', 'return-overlay.img', 'sc8280xp-huawei-gaokun3.dtb'}
    selected = []
    for name in sorted(files):
        parts = name.split('/')
        if len(parts) != 2 or not re.fullmatch(r'native-original-graphics-\d{3}', parts[0]):
            continue
        if parts[1] not in allowed:
            continue
        # Conservatively retain the entire directory if any config mentions it.
        if ('/' + parts[0] + '/').casefold() not in texts:
            selected.append(name)
    return selected


payload = r'''
from pathlib import Path
import hashlib,json,os,re,shutil,subprocess
esp=Path('/boot/efi')
root=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/efi-unreferenced-cleanup-001')
default='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
def command(args):return subprocess.check_output(args,text=True,timeout=30)
def sha(path):
 with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write_new(path,data):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
def configs_now():
 return {str(p.relative_to(esp)):p.read_text(errors='replace') for p in esp.rglob('*')
         if p.is_file() and p.suffix.lower() in ['.conf','.cfg','.nsh','.lst','.txt']}
def check_state():
 status=command(['bootctl','status','--no-pager'])
 assert 'Current Entry: '+default in status and 'Default Entry: '+default in status
 assert 'OneShot Entry:' not in status
 assert subprocess.run(['systemctl','is-enabled','harmony-lab-screen-off-001.timer'],capture_output=True,text=True).stdout.strip()=='disabled'
 assert subprocess.run(['systemctl','is-active','harmony-lab-screen-off-001.timer'],capture_output=True,text=True).stdout.strip()=='inactive'
 return status
assert command(['findmnt','-n','-o','SOURCE,FSTYPE','--target',str(esp)]).split()==['/dev/nvme0n1p1','vfat']
assert command(['findmnt','-n','-o','PARTUUID','--target',str(esp)]).strip()=='922f37b2-3474-4761-a370-5aa1dcd7c476'
status=check_state();config=configs_now()
files={str(p.relative_to(esp)):p.stat().st_size for p in esp.rglob('*') if p.is_file()}
selected=candidate_paths(files,config)
assert selected and all(not (esp/n).is_symlink() for n in selected)
total=sum(files[n] for n in selected)
before_free=shutil.disk_usage(esp).free
plan=dict(selected=selected,bytes=total,efi_free_before=before_free,
          boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
          all_boot_entries_retained=True,ubuntu_default_unchanged=True,
          referenced_directories_excluded=True,backup=str(root/'files'),apply=apply)
if not apply:
 print(json.dumps(plan,indent=2))
else:
 assert not root.exists()
 assert total>100*1024**2 and shutil.disk_usage(root.parent).free>total+1024**3
 before={n:sha(esp/n) for n in files}
 firmware=command(['efibootmgr','-v'])
 root.mkdir()
 write_new(root/'before.json',json.dumps(dict(plan=plan,efi_hashes=before,configs=config,firmware=firmware,status=status),indent=2).encode())
 for name in selected:
  source=esp/name;backup=root/'files'/name
  assert sha(source)==before[name]
  backup.parent.mkdir(parents=True,exist_ok=True)
  with source.open('rb') as src,backup.open('xb') as dst:
   shutil.copyfileobj(src,dst);dst.flush();os.fsync(dst.fileno())
  assert sha(backup)==before[name]
 # Complete, durable backups and unchanged live references are required BEFORE deletion.
 os.sync()
 check_state();assert configs_now()==config
 assert candidate_paths(files,configs_now())==selected
 assert command(['efibootmgr','-v'])==firmware
 for name in selected:assert sha(esp/name)==before[name] and sha(root/'files'/name)==before[name]
 write_new(root/'backups-verified.json',json.dumps({n:before[n] for n in selected},indent=2).encode())
 for name in selected:
  (esp/name).unlink()
 os.sync()
 check_state();assert configs_now()==config
 assert command(['efibootmgr','-v'])==firmware
 for name,digest in before.items():
  if name in selected:assert not (esp/name).exists() and sha(root/'files'/name)==digest
  else:assert sha(esp/name)==digest,name
 after_free=shutil.disk_usage(esp).free
 assert after_free>before_free+100*1024**2
 result=dict(plan,efi_free_after=after_free,efi_free_gained=after_free-before_free,
             removed_count=len(selected),other_efi_files_unchanged=len(before)-len(selected),
             backup_hashes_verified=True,all_boot_configs_unchanged=True,firmware_unchanged=True,
             screenoff_timer_disabled_inactive=True,reboot_requested=False,one_shot_selected=False)
 write_new(root/'result.json',json.dumps(result,indent=2).encode())
 print(json.dumps(result,indent=2))
'''


if __name__ == '__main__':
    assert sys.argv[1:] in [[], ['--apply']]
    apply = sys.argv[1:] == ['--apply']
    script = 'apply=' + repr(apply) + '\n' + inspect.getsource(candidate_paths) + '\n' + payload
    # re is needed by the injected helper before the remote payload imports execute.
    script = 'import re\n' + script
    result = subprocess.run(['ssh', '-o', 'HostName=10.126.126.14', '-o',
        'HostKeyAlias=192.168.10.128', '-o', 'ConnectTimeout=10',
        'matebook', 'sudo -n python3 -'], input=script, text=True,
        capture_output=True, timeout=240)
    report = Path(__file__).resolve().parent.parent/'reports/efi-unreferenced-cleanup-001'
    report.mkdir(exist_ok=True)
    stem = 'cleanup' if apply else 'plan'
    for suffix, value in [('stdout', result.stdout), ('stderr', result.stderr)]:
        with (report/(stem+'.'+suffix)).open('x') as f: f.write(value)
    result.check_returncode()
    data = json.loads(result.stdout)
    with (report/(stem+'.json')).open('x') as f: json.dump(data, f, indent=2)
    print(result.stdout)
