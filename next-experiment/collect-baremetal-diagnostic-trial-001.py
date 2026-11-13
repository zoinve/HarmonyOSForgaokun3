"""One delayed SSH attempt after the diagnostic; no retry loop or reboot."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import time

base = Path(__file__).resolve().parent.parent
out = base / 'reports/baremetal-native-trial-001-evidence'
payload = r'''
from pathlib import Path
import base64,hashlib,json,os,subprocess
def run(args): return subprocess.run(args,capture_output=True,text=True,timeout=30)
assert 'harmony.diag=1' not in Path('/proc/cmdline').read_text()
device='/dev/nvme0n1p4';lab=Path('/mnt/harmony-lab')
identity=run(['blkid','-p','-o','export',device]);assert identity.returncode==0
fields=dict(line.split('=',1) for line in identity.stdout.splitlines() if '=' in line)
assert fields['UUID']=='00029cdd-1748-4d2f-b73b-8e8164922098'
assert fields['PART_ENTRY_UUID']=='24bd14b9-9d92-490a-ad15-a59c6b8e7cd9'
assert fields['TYPE']=='ext4'
mounted_here=False
mounted=run(['findmnt','-n','-o','SOURCE','--mountpoint',str(lab)])
if mounted.returncode:
    assert lab.is_dir() and not lab.is_symlink()
    assert not any(lab.iterdir()),'Refuse to cover files in an unmounted lab directory'
    r=run(['mount','-t','ext4','-o','ro,noload,nodev,nosuid,noexec',device,str(lab)])
    assert r.returncode==0,r.stderr
    mounted_here=True
assert run(['findmnt','-n','-o','SOURCE,UUID','--target',str(lab)]).stdout.split()==[device,fields['UUID']]
before=json.loads((lab/'work/native-trial-001/before-reboot.json').read_text())
boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
files=[];total=0
for directory in sorted(lab.glob('native-diag-001-*')):
    assert directory.is_dir() and not directory.is_symlink()
    for path in sorted(directory.glob('phase-*.log')):
        assert path.is_file() and not path.is_symlink() and path.stat().st_size<=16*1024**2
        data=path.read_bytes();total+=len(data);assert total<=64*1024**2
        files.append(dict(path=str(path.relative_to(lab)),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),data_b64=base64.b64encode(data).decode()))
backup=lab/'work/boot-entry-install-001'
old=json.loads((backup/'efi-files-before.json').read_text())
esp=Path('/boot/efi')
changes=[]
for rel,digest in old.items():
    p=esp/rel
    actual=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
    if actual!=digest: changes.append(dict(path=rel,expected_sha256=digest,actual_sha256=actual))
entries=run(['bootctl','list','--json=short','--no-pager']);assert entries.returncode==0
firmware=run(['efibootmgr','-v'])
result=dict(before=before,after_boot_id=boot_id,boot_id_changed=boot_id!=before['before_boot_id'],
            running_kernel=os.uname().release,cmdline=Path('/proc/cmdline').read_text().strip(),
            files=files,log_file_count=len(files),original_efi_file_changes=changes,
            boot_entries=json.loads(entries.stdout),firmware_boot_entries=firmware.stdout,
            diagnostic_entry_files=[p.name for p in (esp/'loader/entries').glob('harmony-native-diag-004*')],
            lab_mounted_read_only_by_collector=mounted_here,native_diagnostic_success_not_inferred=True,
            harmony_boot_attempted=False)
print(json.dumps(result))
'''
compile(payload, 'trial-collect-remote', 'exec')
if __name__ == '__main__':
    assert not out.exists()
    out.mkdir()
    # A single scheduled check, not periodic connection polling.
    time.sleep(300)
    r = subprocess.run(['ssh', '-o', 'ConnectTimeout=15', '-o', 'ConnectionAttempts=1',
                        'matebook', 'sudo -n python3 -'], input=payload,
                       text=True, capture_output=True, timeout=180)
    (out / 'ssh.stderr').write_text(r.stderr, encoding='utf-8')
    if r.returncode:
        (out / 'collection-failed.json').write_text(json.dumps(dict(returncode=r.returncode,
            stderr=r.stderr,stdout=r.stdout,retry_attempted=False),indent=2),encoding='utf-8')
        print(json.dumps(dict(collection_succeeded=False,ssh_returncode=r.returncode,
            stderr=r.stderr,retry_attempted=False),indent=2))
    else:
        result = json.loads(r.stdout)
        for row in result['files']:
            relative = Path(row['path'])
            assert not relative.is_absolute() and '..' not in relative.parts
            data = base64.b64decode(row.pop('data_b64'), validate=True)
            assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
            target = out / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as stream: stream.write(data)
        (out / 'collection.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        print(json.dumps({k:result[k] for k in ('boot_id_changed','running_kernel',
            'log_file_count','diagnostic_entry_files','original_efi_file_changes',
            'lab_mounted_read_only_by_collector')},indent=2))
