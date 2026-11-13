"""Stage inert files and verify refusal guards; never launch PID1 or reboot."""
import json, subprocess
from pathlib import Path

remote = r'''
import hashlib,io,json,os,subprocess,sys,tarfile
from pathlib import Path
root=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/native-original-graphics-boot-001')
assert not root.exists()
with tarfile.open(fileobj=io.BytesIO(sys.stdin.buffer.read()),mode='r:gz') as tar:
 members=tar.getmembers()
 assert len(members)==10
 assert all(m.isfile() and '/' not in m.name and m.name not in ['.','..'] for m in members)
 root.mkdir(mode=0o700)
 for m in members:
  with (root/m.name).open('xb') as f:
   f.write(tar.extractfile(m).read());f.flush();os.fsync(f.fileno())
d=json.loads((root/'result.json').read_text())
for row in d['artifacts']:
 p=root/row['name']
 with p.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
 assert h==row['sha256'] and p.stat().st_size==row['bytes']
guards=[]
for name in ['init','bootstrap']:
 p=root/name;p.chmod(0o700)
 r=subprocess.run([str(p)],capture_output=True,text=True,timeout=5)
 assert r.returncode==77 and 'requires' in r.stderr
 guards.append(dict(name=name,exit_code=r.returncode,stderr=r.stderr))
print(json.dumps(dict(staged_files=len(members),guard_checks=guards,runtime_launched=False)))
'''
if __name__ == '__main__':
    dest=Path('reports/native-original-graphics-boot-001/stage-result.json')
    assert not dest.exists()
    names=['result.json','initrd.img','linux','sc8280xp-huawei-gaokun3.dtb','init','bootstrap','init.c','bootstrap.c','board-init.cfg','board-fstab']
    data=subprocess.check_output(['wsl','-d','Debian','--','tar','-czf','-','-C','/home/zoinve/harmony-virgl-883/native-original-graphics-boot-001',*names],timeout=180)
    import base64
    encoded=base64.b64encode(remote.encode()).decode()
    cmd="python3 -c \"import base64;exec(base64.b64decode('"+encoded+"'))\""
    r=subprocess.run(['ssh','matebook',cmd],input=data,capture_output=True,timeout=180)
    assert r.returncode==0,r.stderr.decode(errors='replace')
    result=json.loads(r.stdout)
    with dest.open('x') as f:json.dump(result,f,indent=2)
    print(json.dumps(result,indent=2))
