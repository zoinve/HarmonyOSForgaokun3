"""Copy new diagnostic assets only into the isolated lab, then verify ARM64 refusals."""
from pathlib import Path
import hashlib
import json
import subprocess

base=Path(__file__).resolve().parent.parent
report=base/'reports/baremetal-identity-diagnostic-008-staged.json'
work='/home/zoinve/harmony-virgl-883'
remote='/mnt/harmony-lab/work/native-identity-diagnostic-008'
diagnostic=json.loads((base/'reports/baremetal-diagnostic-init-008/result.json').read_text())
rows=[
    dict(name='linux',path=work+'/baremetal-identity-native-package-001/linux',sha256=diagnostic['kernel_sha256']),
    dict(name='sc8280xp-huawei-gaokun3.dtb',path=work+'/baremetal-identity-native-package-001/sc8280xp-huawei-gaokun3.dtb',sha256=diagnostic['dtb_sha256']),
    dict(name='diagnostic-init.cpio.gz',path=diagnostic['archive'],sha256=diagnostic['archive_sha256']),
    dict(name='diagnostic-init',path=work+'/baremetal-diagnostic-init-008/init',sha256=diagnostic['binary_sha256']),
    dict(name='native-identity-read-001',path=work+'/baremetal-identity-native-read-009/sdk/native-probe',sha256=diagnostic['helper_sha256']),
]
guard='remote='+repr(remote)+'\n'+r'''
from pathlib import Path
import subprocess
assert 'harmony.diag=1' not in Path('/proc/cmdline').read_text().split()
assert subprocess.check_output(['findmnt','-n','-o','SOURCE,UUID','--target','/mnt/harmony-lab'],text=True).split()==['/dev/nvme0n1p4','00029cdd-1748-4d2f-b73b-8e8164922098']
assert 'rw' in subprocess.check_output(['findmnt','-n','-o','OPTIONS','--target','/mnt/harmony-lab'],text=True).strip().split(',')
p=Path(remote);assert not p.exists();p.mkdir()
'''
payload='remote='+repr(remote)+'\nrows='+repr(rows)+'\n'+r'''
from pathlib import Path
import gzip,hashlib,json,subprocess,os
dest=Path(remote)
for row in rows:
 p=dest/row['name'];assert not p.is_symlink() and p.is_file()
 assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256'];row['bytes']=p.stat().st_size;row['remote_path']=str(p)
checks=[]
for name,marker in [('diagnostic-init','requires PID 1'),('native-identity-read-001','requires diagnostic kernel and opt-in')]:
 p=dest/name;p.chmod(0o755)
 r=subprocess.run([str(p)],capture_output=True,text=True,timeout=5)
 assert r.returncode==77 and marker in r.stderr,(name,r.returncode,r.stdout,r.stderr)
 checks.append(dict(name=name,returncode=r.returncode,stderr=r.stderr))
assert len(gzip.decompress((dest/'diagnostic-init.cpio.gz').read_bytes()))>24*1024*1024
os.sync()
d=dict(destination=remote,files=rows,arm64_refusal_checks=checks,non_pid1_refusal_verified=True,boot_entries_modified=False,reboot_requested=False)
(dest/'manifest.json').write_text(json.dumps(d,indent=2)+'\n');os.sync();print(json.dumps(d,indent=2))
'''
compile(guard,'stage008-guard','exec');compile(payload,'stage008-audit','exec')
if __name__=='__main__':
    assert not report.exists()
    for row in rows:
        p=Path('//wsl.localhost/Debian'+row['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
    subprocess.run(['ssh','-o','ConnectTimeout=3','matebook','python3 -'],input=guard,text=True,check=True,timeout=30)
    for row in rows:subprocess.run(['scp','-o','ConnectTimeout=3',str(Path('//wsl.localhost/Debian'+row['path'])),'matebook:'+remote+'/'+row['name']],check=True,timeout=120)
    r=subprocess.run(['ssh','-o','ConnectTimeout=3','matebook','sudo -n python3 -'],input=payload,capture_output=True,text=True,timeout=90)
    assert r.returncode==0,r.stderr
    d=json.loads(r.stdout);report.write_text(json.dumps(d,indent=2)+'\n');print(r.stdout)
