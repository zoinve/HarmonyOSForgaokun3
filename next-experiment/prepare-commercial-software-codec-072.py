"""Extract matching development packages privately; never install host packages."""
from pathlib import Path
import json
import runpy
import subprocess

base = Path(__file__).resolve().parent
out = base.parent / 'reports/commercial-software-codec-prepare-072'
out.mkdir()
workflow = runpy.run_path(str(base / 'commercial-workflow-071.py'))
workflow['configure_local_transport']()
code = r'''
from pathlib import Path
import hashlib,json,subprocess
root=Path.home()/'.local/share/harmony-arm64-kvm-lab/software-codec-build-072'
root.mkdir(mode=0o700)
packages=root/'packages';packages.mkdir()
sysroot=root/'sysroot';sysroot.mkdir()
boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
timer=['systemctl','is-active','harmony-lab-screen-off-001.timer']
assert subprocess.check_output(timer,text=True).strip()=='active'
before=subprocess.check_output(['dpkg-query','-W'],text=True)
rows=[]
for name in ['libavcodec-dev','libavutil-dev']:
 version=subprocess.check_output(['dpkg-query','-W','-f=${Version}',name.replace('-dev','62' if name=='libavcodec-dev' else '60')],text=True)
 run=subprocess.run(['apt-get','download',name+'='+version],cwd=packages,capture_output=True,text=True,timeout=180)
 assert run.returncode==0,(run.stdout,run.stderr)
 matches=list(packages.glob(name+'_*.deb'));assert len(matches)==1
 package=matches[0]
 subprocess.run(['dpkg-deb','--extract',str(package),str(sysroot)],check=True,timeout=60)
 rows.append(dict(package=name,version=version,sha256=hashlib.sha256(package.read_bytes()).hexdigest(),bytes=package.stat().st_size,download_stderr=run.stderr))
headers=sysroot/'usr/include/aarch64-linux-gnu'
assert (headers/'libavcodec/avcodec.h').is_file()
assert (headers/'libavutil/frame.h').is_file()
deps=subprocess.check_output(['ldd','/usr/lib/aarch64-linux-gnu/libavcodec.so.62'],text=True)
assert 'not found' not in deps
assert subprocess.check_output(['dpkg-query','-W'],text=True)==before
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==boot
assert subprocess.check_output(timer,text=True).strip()=='active'
result=dict(workdir=str(root),boot_id=boot,packages=rows,headers=str(headers),runtime_dependencies=deps,packages_installed=False,package_database_unchanged=True,host_rebooted=False,desktop_verified=False)
with (root/'preparation.json').open('x') as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
'''
run = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
    '-o', 'HostName=192.168.10.128', '-o', 'HostKeyAlias=192.168.10.128',
    '-o', 'ConnectTimeout=10', 'matebook', 'python3 -'], input=code,
    text=True, capture_output=True, timeout=500)
(out / 'ssh.stdout').open('x').write(run.stdout)
(out / 'ssh.stderr').open('x').write(run.stderr)
assert run.returncode == 0, run.stderr
result = json.loads(run.stdout)
(out / 'result.json').open('x').write(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
