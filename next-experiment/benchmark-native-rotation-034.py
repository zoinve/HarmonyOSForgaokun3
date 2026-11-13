"""Run a bounded userspace-only ARM64 benchmark; no graphics/boot configuration writes."""
from pathlib import Path
import subprocess,hashlib,base64,json
base=Path(__file__).resolve().parent.parent
dest=base/'reports/native-render-034/arm64-rotation-benchmark.json'
assert not dest.exists()
blob=subprocess.check_output(['wsl','-d','Debian','--','cat','/home/zoinve/harmony-virgl-883/native-rotation-034-tests/rotation-arm64'])
payload='blob='+repr(base64.b64encode(blob).decode())+'\nexpected='+repr(hashlib.sha256(blob).hexdigest())+'\n'+r'''
from pathlib import Path
import base64,hashlib,json,subprocess,os,time
assert subprocess.check_output(['uname','-r'],text=True).strip()=='7.1.0-rc3-gaokun3+'
root=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/native-rotation-034-benchmark')
assert not root.exists();root.mkdir()
data=base64.b64decode(blob);assert hashlib.sha256(data).hexdigest()==expected
p=root/'rotation-arm64'
with p.open('xb') as f:f.write(data)
p.chmod(0o700)
before=Path('/proc/loadavg').read_text().strip()
r=subprocess.run([str(p),'benchmark'],text=True,capture_output=True,timeout=60)
with (root/'stdout.txt').open('x') as f:f.write(r.stdout)
with (root/'stderr.txt').open('x') as f:f.write(r.stderr)
assert r.returncode==0,(r.returncode,r.stderr)
d=json.loads(r.stdout);assert d['pixel_equivalence'] and d['neon']
d.update(binary_sha256=expected,load_before=before,load_after=Path('/proc/loadavg').read_text().strip(),
 uname=subprocess.check_output(['uname','-a'],text=True).strip(),boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
 iterations_per_path=24,logical_width=2560,logical_height=1600,
 cached_ram_microbenchmark_only=True,gpu_acceleration=False,desktop_fps_verified=False)
with (root/'result.json').open('x') as f:json.dump(d,f,indent=2)
print(json.dumps(d,indent=2))
'''
r=subprocess.run(['ssh','matebook','python3 -'],input=payload,text=True,capture_output=True,timeout=90)
with dest.with_suffix('.stdout').open('x') as f:f.write(r.stdout)
with dest.with_suffix('.stderr').open('x') as f:f.write(r.stderr)
r.check_returncode()
with dest.open('x') as f:json.dump(json.loads(r.stdout),f,indent=2)
print(r.stdout)
