"""Install one kernel490/P2P502 candidate, preserving Ubuntu and desktop173."""
from pathlib import Path
import base64
import datetime
import hashlib
import json
import runpy
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/commercial61-native-502'
WORKFLOW = runpy.run_path(str(ROOT / 'next-experiment/settings-workflow-254.py'))
INSTALL = r'''
import base64,shutil
esp=Path('/boot/efi');entries=esp/'loader/entries'
work=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/commercial61-native-502')
entry=entries/'commercial61-native-502.conf';image=esp/'set502.img'
kernel=esp/'native-compat-kernel-490'
old_entry=entries/'commercial61-native-471.conf'
assert not work.exists() and not entry.exists() and not image.exists() and not kernel.exists()
assert old_entry.is_file() and (entries/'commercial61-native-173.conf').is_file()
assert (entries/'harmonyos-gpu-manual.conf').is_file()
old=old_entry.read_text()
assert old.count('linux /native-original-graphics-045/linux')==1 and old.count('/set471.img')==1
new=old.replace('linux /native-original-graphics-045/linux','linux /native-compat-kernel-490/linux').replace('/set471.img','/set502.img')
new='\n'.join('title native P2P and compatibility kernel 502 - AUTO RETURN 900 SEC' if line.startswith('title ') else line for line in new.splitlines())+'\n'
decoded={name:base64.b64decode(row['base64'],validate=True) for name,row in payload.items()}
for name,data in decoded.items():assert hashlib.sha256(data).hexdigest()==payload[name]['sha256']
assert shutil.disk_usage(esp).free>len(decoded['initrd.img'])+len(decoded['kernel490'])+32*1024**2+131072
firmware=command(['efibootmgr','-v'])
work.mkdir(mode=0o700)
def write(path,data,mode):
 with path.open('xb') as stream:
  stream.write(data);stream.flush();os.fsync(stream.fileno())
 if path.is_relative_to(work):path.chmod(mode)
for name,data in decoded.items():
 if name!='kernel490':write(work/name,data,0o600 if name=='initrd.img' else 0o755)
kernel.mkdir()
write(kernel/'linux',decoded['kernel490'],0o600)
write(image,decoded['initrd.img'],0o600)
for path,name in [(kernel/'linux','kernel490'),(image,'initrd.img')]:
 with path.open('rb') as stream:assert hashlib.file_digest(stream,'sha256').hexdigest()==payload[name]['sha256']
write(entry,new.encode(),0o600)
archive=dict(name=old_entry.name,content=old,sha256=hashlib.sha256(old.encode()).hexdigest(),
 kept_experiments=['commercial61-native-173.conf','commercial61-native-502.conf'],user_authorized_retention=True)
write(work/'retired-entry-471.json',json.dumps(archive,indent=2).encode(),0o600)
assert old_entry.read_text()==old
old_entry.unlink()
assert command(['efibootmgr','-v'])==firmware
subprocess.run(['sync','-f',str(esp)],check=True,timeout=30)
result=dict(installed=True,entry=entry.name,kernel='/native-compat-kernel-490/linux',
 kernel_sha256=payload['kernel490']['sha256'],initrd_sha256=payload['initrd.img']['sha256'],
 desktop173_retained=True,prior471_entry_archived_removed=True,
 ubuntu_default_preserved=True,screenoff_timer_enabled_active=True,
 active165_written=False,settings_candidate_written=False,original_images_written=False,
 matching_modules_packaged=True,free=shutil.disk_usage(esp).free,
 boot_requested=False,runtime_verified=False,huawei_share_transfer_verified=False)
write(work/'installation-result.json',json.dumps(result,indent=2).encode(),0o600)
print(json.dumps(result,indent=2))
'''


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ['install','boot']
    if sys.argv[1] == 'install':
        assert not (REPORT / 'installation-result.json').exists()
        rows = {row['name']:row for row in json.loads((REPORT / 'result.json').read_text())['artifacts']}
        overlay = json.loads((REPORT / 'overlay-result.json').read_text())
        kernel = json.loads((ROOT / 'reports/compat-kernel-490/result.json').read_text())
        payload = {}
        for name in ['init','bootstrap','bootstrap-runtime087','initrd.img','kernel490']:
            if name == 'kernel490':
                source, expected = kernel['image'], kernel['sha256']
            else:
                source = '/home/zoinve/harmony-virgl-883/commercial61-native-502/' + (
                    'minimal-overlay.img' if name == 'initrd.img' else name)
                expected = overlay['sha256'] if name == 'initrd.img' else rows[name]['sha256']
            data = subprocess.check_output(['wsl','-d','Debian','--','cat',source])
            assert hashlib.sha256(data).hexdigest() == expected
            payload[name] = dict(base64=base64.b64encode(data).decode(),sha256=expected)
        text = WORKFLOW['remote']('payload=' + repr(payload) + '\n' + WORKFLOW['GUARD'] + INSTALL,timeout=240)
        (REPORT / 'installation-result.json').open('x').write(text)
        print(text)
    else:
        assert (REPORT / 'installation-result.json').exists()
        record = REPORT / 'boot-attempt.json'
        assert not record.exists(), 'one attempt only'
        state = json.loads(WORKFLOW['remote'](WORKFLOW['GUARD'] +
            "\nprint(json.dumps(dict(boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip())))"))
        record.open('x').write(json.dumps(dict(start_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            before_boot_id=state['boot_id'],entry='commercial61-native-502.conf',attempt_count=1,
            huawei_share_transfer_verified=False),indent=2))
        code = "import subprocess;from pathlib import Path;assert Path('/boot/efi/loader/entries/commercial61-native-502.conf').is_file();subprocess.run(['bootctl','set-oneshot','commercial61-native-502.conf'],check=True);subprocess.run(['systemctl','reboot'],check=True)"
        result = subprocess.run(WORKFLOW['SSH'] + ['sudo -n python3 -'],input=code,text=True,
                                capture_output=True,timeout=40)
        outcome = dict(reboot_command_exit=result.returncode,stdout=result.stdout,stderr=result.stderr,
                       returned_to_ubuntu=False,no_retry_requested=True)
        (REPORT / 'boot-command.json').open('x').write(json.dumps(outcome,indent=2))
        print(json.dumps(outcome,indent=2))
