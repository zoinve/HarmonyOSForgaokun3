"""Add one hash-pinned target kernel without replacing any existing EFI file."""
from pathlib import Path
import base64
import hashlib
import json
import runpy
import subprocess

base = Path(__file__).resolve().parents[1]
report = base / 'reports/native-binder-kernel-045'
result = json.loads((report / 'result.json').read_text())
data = Path(result['image']).read_bytes()
assert hashlib.sha256(data).hexdigest() == result['sha256']
assert result['old_source_config_unchanged'] and result['original_tokens_uid_checks_unchanged']
code = 'data=' + repr(base64.b64encode(data).decode()) + '\nexpected=' + repr(result['sha256']) + '\n' + r'''
from pathlib import Path
import base64,hashlib,json,os,shutil,subprocess
esp=Path('/boot/efi');dest=esp/'native-original-graphics-045'
work=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/native-binder-kernel-045')
assert not work.exists() and not dest.exists()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
status=subprocess.check_output(['bootctl','status','--no-pager'],text=True)
default='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
assert ('Default Entry: '+default) in status and ('Current Entry: '+default) in status and 'OneShot Entry:' not in status
assert subprocess.run(['systemctl','is-enabled','harmony-lab-screen-off-001.timer'],capture_output=True,text=True).stdout.strip()=='enabled'
assert subprocess.run(['systemctl','is-active','harmony-lab-screen-off-001.timer'],capture_output=True,text=True).stdout.strip()=='active'
assert not subprocess.run(['findmnt','-rn','-S','/dev/nvme0n1p4'],capture_output=True,text=True).stdout.strip()
assert sha(esp/'native-original-graphics-031/linux')=='6fa44a5f1996a82bc95e8c44b3d32a69cc14d3789e39cffa2fcafafb7c294ff5'
blob=base64.b64decode(data);assert hashlib.sha256(blob).hexdigest()==expected
assert shutil.disk_usage(esp).free>len(blob)+34*1024**2
before={str(p.relative_to(esp)):sha(p) for p in esp.rglob('*') if p.is_file()}
firmware=subprocess.check_output(['efibootmgr','-v'],text=True)
work.mkdir(mode=0o700)
with (work/'installation-journal.json').open('x') as f:
 json.dump(dict(efi_before=before,firmware=firmware,status=status),f,indent=2);f.flush();os.fsync(f.fileno())
dest.mkdir()
with (dest/'linux').open('xb') as f:
 f.write(blob);f.flush();os.fsync(f.fileno())
os.sync()
assert sha(dest/'linux')==expected
assert all(sha(esp/n)==h for n,h in before.items())
assert subprocess.check_output(['efibootmgr','-v'],text=True)==firmware
assert subprocess.check_output(['bootctl','status','--no-pager'],text=True)==status
out=dict(kernel=str(dest/'linux'),sha256=expected,bytes=len(blob),prior_efi_files_unchanged=len(before),ubuntu_current_default_unchanged=True,firmware_unchanged=True,boot_entry_installed=False,reboot_requested=False)
with (work/'installation-result.json').open('x') as f:json.dump(out,f,indent=2)
print(json.dumps(out,indent=2))
'''
w = runpy.run_path(str(base / 'next-experiment/commercial-workflow-045.py'))
w['configure_local_transport']()
r = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
                    '-o', 'HostName=192.168.10.128', '-o', 'HostKeyAlias=192.168.10.128',
                    '-o', 'ConnectTimeout=10', 'matebook', 'sudo -n python3 -'],
                   input=code, text=True, capture_output=True, timeout=400)
with (report / 'installation.stdout').open('x') as f:f.write(r.stdout)
with (report / 'installation.stderr').open('x') as f:f.write(r.stderr)
assert r.returncode == 0, r.stderr
with (report / 'installation-result.json').open('x') as f:f.write(r.stdout)
print(r.stdout)
