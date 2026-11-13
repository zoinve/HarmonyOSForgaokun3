"""Compile an OHOS CPU-only fd probe and run unprivileged, without GPU access or reboots."""
from pathlib import Path
import hashlib
import json
import subprocess

base=Path(__file__).resolve().parent.parent
out=base/'reports/baremetal-fd-identity-probe-001'
assert not out.exists()
out.mkdir()
source=(base/'next-experiment/baremetal-fd-identity-probe-001.c').read_text()
payload='source='+repr(source)+'\n'+r'''
from pathlib import Path
import subprocess,json,hashlib
root=Path('/home/zoinve/harmony-virgl-883');work=root/'baremetal-fd-identity-probe-001'
assert not work.exists();work.mkdir();(work/'probe.c').write_text(source)
r=subprocess.run([str(root/'toolchain/ohos-cc'),'-O2','-Wall','-Wextra','-Werror',str(work/'probe.c'),'-o',str(work/'probe')],capture_output=True,text=True,timeout=30)
(work/'compile.stdout').write_text(r.stdout);(work/'compile.stderr').write_text(r.stderr);r.check_returncode()
print(json.dumps(dict(path=str(work/'probe'),sha256=hashlib.sha256((work/'probe').read_bytes()).hexdigest(),bytes=(work/'probe').stat().st_size,source_sha256=hashlib.sha256(source.encode()).hexdigest())))
'''
r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,capture_output=True,timeout=60)
(out/'compile.stdout').write_text(r.stdout);(out/'compile.stderr').write_text(r.stderr);r.check_returncode()
expected=json.loads(r.stdout)
r=subprocess.run(['ssh','-o','ConnectTimeout=3','matebook','python3 -'],input="from pathlib import Path;p=Path('/home/zoinve/harmony-lab-fd-identity-transfer-001');assert not p.exists();p.mkdir(mode=0o700)",text=True,capture_output=True,timeout=15);r.check_returncode()
local='\\\\wsl.localhost\\Debian'+expected['path'].replace('/','\\')
subprocess.run(['scp',local,'matebook:/home/zoinve/harmony-lab-fd-identity-transfer-001/probe'],check=True,timeout=30)
remote='expected='+repr(expected)+'\n'+r'''
from pathlib import Path
import hashlib,json,subprocess,os
assert os.uname().release=='7.1.0-rc3-gaokun3+'
assert 'harmony.diag=1' not in Path('/proc/cmdline').read_text().split()
stage=Path('/var/lib/harmony-lab-fd-identity-probe-001');assert not stage.exists()
data=Path('/home/zoinve/harmony-lab-fd-identity-transfer-001/probe').read_bytes();assert len(data)==expected['bytes'] and hashlib.sha256(data).hexdigest()==expected['sha256']
loader=Path('/var/lib/harmony-lab-freedreno-fence-001/lib/ld-musl-aarch64.so.1')
assert hashlib.sha256(loader.read_bytes()).hexdigest()=='f7947b746dc4169677321b18ee77e4f4f158fde75762b2d9a3ae107b277c0181'
stage.mkdir(mode=0o755);(stage/'probe').write_bytes(data);(stage/'probe').chmod(0o555)
args=['systemd-run','--quiet','--wait','--pipe','--unit=harmony-lab-fd-identity-probe-001',
      '-p','Type=exec','-p','User=zoinve','-p','NoNewPrivileges=yes','-p','CapabilityBoundingSet=',
      '-p','PrivateDevices=yes','-p','PrivateNetwork=yes','-p','ProtectSystem=strict',
      '-p','ProtectHome=yes','-p','PrivateTmp=yes','-p','RuntimeMaxSec=10','-p','LimitCORE=0',
      '-p','MemoryMax=64M','-p','TasksMax=8',str(loader),'--library-path',str(loader.parent),str(stage/'probe')]
before=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
r=subprocess.run(args,capture_output=True,text=True,timeout=25)
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==before
print(json.dumps(dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr,command=args,
    boot_id=before,probe_sha256=hashlib.sha256((stage/'probe').read_bytes()).hexdigest(),
    gpu_tested=False,reboot_requested=False,security_permissions_relaxed=False)))
'''
compile(remote,'fd-identity001-remote','exec')
r=subprocess.run(['ssh','-o','ConnectTimeout=3','matebook','sudo -n python3 -'],input=remote,text=True,capture_output=True,timeout=50)
(out/'remote.stdout').write_text(r.stdout);(out/'remote.stderr').write_text(r.stderr);r.check_returncode()
result=json.loads(r.stdout);(out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
