"""One bounded offscreen GPU probe. No KMS modeset or host configuration change."""
from pathlib import Path
import subprocess,hashlib,base64,json
base=Path(__file__).resolve().parent.parent
local=base/'reports/native-gpu-probe-036';local.mkdir(exist_ok=False)
blob=subprocess.check_output(['wsl','-d','Debian','--','cat','/home/zoinve/harmony-virgl-883/native-gpu-probe-036/gpu-probe'])
payload='blob='+repr(base64.b64encode(blob).decode())+'\nexpected='+repr(hashlib.sha256(blob).hexdigest())+'\n'+r'''
from pathlib import Path
import base64,hashlib,json,subprocess
assert subprocess.check_output(['uname','-r'],text=True).strip()=='7.1.0-rc3-gaokun3+'
root=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/native-gpu-probe-036')
root.mkdir(exist_ok=False)
data=base64.b64decode(blob);assert hashlib.sha256(data).hexdigest()==expected
p=root/'gpu-probe'
with p.open('xb') as f:f.write(data)
p.chmod(0o700)
r=subprocess.run(['sudo','-n','timeout','60',str(p)],text=True,capture_output=True,timeout=70)
for name,text in [('stdout.txt',r.stdout),('stderr.txt',r.stderr)]:
 with (root/name).open('x') as f:f.write(text)
d=dict(exit_code=r.returncode,stdout=r.stdout,stderr=r.stderr,binary_sha256=expected,
 boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
 hardware_pixels_passed=r.returncode==0 and 'PASS: hardware rotation' in r.stdout,
 offscreen_only=True,kms_modeset=False,host_configuration_changed=False,
 harmony_service_runtime_verified=False,desktop_fps_verified=False)
with (root/'result.json').open('x') as f:json.dump(d,f,indent=2)
print(json.dumps(d,indent=2))
'''
r=subprocess.run(['ssh','matebook','python3 -'],input=payload,text=True,capture_output=True,timeout=90)
for name,text in [('ssh.stdout',r.stdout),('ssh.stderr',r.stderr)]:
 with (local/name).open('x') as f:f.write(text)
r.check_returncode();d=json.loads(r.stdout)
with (local/'result.json').open('x') as f:json.dump(d,f,indent=2)
print(json.dumps(d,indent=2))
assert d['hardware_pixels_passed'],'probe failed; original outputs retained, do not deploy GPU pipeline'
