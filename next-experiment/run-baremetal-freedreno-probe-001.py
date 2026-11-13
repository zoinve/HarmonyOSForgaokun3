"""Deploy a hash-checked private bundle and run only an unprivileged render-node test."""
from pathlib import Path
import json
import subprocess

base = Path(__file__).resolve().parent.parent
package = base / 'reports/baremetal-freedreno-probe-package-001'
out = base / 'reports/baremetal-freedreno-probe-run-001'

payload = r'''
from pathlib import Path
import hashlib,io,json,os,stat,subprocess,tarfile
def command(args,timeout=20):
    r=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
    return dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)
def sha(data):return hashlib.sha256(data).hexdigest()
def checked(args):
    r=command(args);assert r['returncode']==0,r;return r['stdout'].strip()
assert os.uname().release=='7.1.0-rc3-gaokun3+'
assert 'harmony.diag=1' not in Path('/proc/cmdline').read_text().split()
boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
node=Path('/dev/dri/renderD128');st=node.stat();assert stat.S_ISCHR(st.st_mode) and (os.major(st.st_rdev),os.minor(st.st_rdev))==(226,128)
assert checked(['systemctl','is-active','harmony-lab-screen-off-001.timer'])=='active'
var=Path('/sys/firmware/efi/efivars');guid='4a67b082-0a4c-41cf-b6c7-440b29bb8c4f'
default=(var/('LoaderEntryDefault-'+guid)).read_bytes()
assert default[4:].decode('utf-16-le').rstrip('\0')=='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'
one=var/('LoaderEntryOneShot-'+guid);assert not one.exists() or not one.read_bytes()[4:].decode('utf-16-le').rstrip('\0')
raw=Path('/home/zoinve/harmony-lab-freedreno-transfer-001/bundle.tar.gz').read_bytes()
assert len(raw)==expected['archive_bytes'] and sha(raw)==expected['archive_sha256']
stage=Path('/var/lib/harmony-lab-freedreno-probe-001');assert not stage.exists();stage.mkdir(mode=0o755)
files={r['path']:r for r in expected['files']};links=expected['symlinks']
with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as tar:
    members={m.name:m for m in tar.getmembers()};assert len(members)==len(tar.getmembers())
    assert set(members)==set(files)|set(links)|{'lib','manifest.json'}
    for name,row in files.items():
        assert name=='probe' or (name.startswith('lib/') and len(Path(name).parts)==2)
        m=members[name];assert m.isfile();data=tar.extractfile(m).read()
        assert len(data)==row['bytes'] and sha(data)==row['sha256'],name
        p=stage/name;p.parent.mkdir(exist_ok=True);p.write_bytes(data);p.chmod(0o555)
    for name,target in links.items():
        assert name=='lib/libc.so' and target=='ld-musl-aarch64.so.1'
        m=members[name];assert m.issym() and m.linkname==target
        (stage/name).symlink_to(target)
    m=members['manifest.json'];assert m.isfile()
    manifest=json.loads(tar.extractfile(m).read());assert manifest['files']==expected['files'] and manifest['symlinks']==links
    (stage/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
os.sync()
props=['User=zoinve','SupplementaryGroups=render','DevicePolicy=closed',
       'DeviceAllow=/dev/dri/renderD128 rw','NoNewPrivileges=yes','CapabilityBoundingSet=',
       'ProtectSystem=strict','ProtectHome=yes','PrivateTmp=yes','PrivateNetwork=yes',
       'RestrictAddressFamilies=AF_UNIX','UMask=0077','RuntimeMaxSec=45',
       'TimeoutStopSec=5','KillMode=control-group','LimitCORE=0','MemoryMax=512M','TasksMax=32']
def service(unit,args):
    cmd=['systemd-run','--unit='+unit,'--wait','--pipe','--service-type=exec']
    for p in props:cmd+=['--property='+p]
    cmd+=['--setenv=HOME=/nonexistent','--setenv=MESA_SHADER_CACHE_DISABLE=true',
          '--setenv=EGL_LOG_LEVEL=debug']+args
    return command(cmd,timeout=65)
security=r"""
import os
assert os.geteuid()==1001
with open('/proc/self/status') as f:status=f.read()
assert 'NoNewPrivs:\t1' in status and 'CapEff:\t0000000000000000' in status
fd=os.open('/dev/dri/renderD128',os.O_RDWR);os.close(fd)
try:os.open('/dev/dri/card0',os.O_RDWR)
except PermissionError:pass
else:raise AssertionError('DRM card0 unexpectedly accessible')
print('RENDER_ONLY_SANDBOX_VERIFIED uid=1001 card0_denied=1 renderD128_allowed=1')
"""
sandbox=service('harmony-lab-freedreno-sandbox-001',['/usr/bin/python3','-c',security])
assert sandbox['returncode']==0,sandbox
before=command(['dmesg','--color=never'])
result=service('harmony-lab-freedreno-probe-001',[str(stage/'lib/ld-musl-aarch64.so.1'),
               '--library-path',str(stage/'lib'),str(stage/'probe')])
properties=command(['systemctl','show','harmony-lab-freedreno-probe-001.service',
 '--property=Result','--property=ExecMainStatus','--property=User','--property=SupplementaryGroups',
 '--property=DevicePolicy','--property=DeviceAllow','--property=NoNewPrivileges',
 '--property=CapabilityBoundingSet','--property=ProtectSystem','--property=ProtectHome'])
after=command(['dmesg','--color=never'])
new_kernel=after['stdout'][len(before['stdout']):] if after['stdout'].startswith(before['stdout']) else None
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==boot
assert (var/('LoaderEntryDefault-'+guid)).read_bytes()==default
verified=[]
for name,row in files.items():assert sha((stage/name).read_bytes())==row['sha256'];verified.append(name)
report=dict(boot_id=boot,kernel=os.uname().release,package_sha256=expected['archive_sha256'],
 stage=str(stage),sandbox=sandbox,requested_service_properties=props,run=result,
 effective_service_properties=properties,new_kernel_log=new_kernel,
 kernel_log_prefix_preserved=new_kernel is not None,bundle_files_verified_unchanged=verified,
 gpu_pixel_test_passed=(result['returncode']==0 and 'FREEDRENO001_PASS shader_triangle_and_readback desktop_not_tested=1' in result['stdout']),
 reboot_requested=False,boot_entries_modified=False,desktop_verified=False,physical_screen_observed=False)
print(json.dumps(report,indent=2),flush=True)
'''

if __name__ == '__main__':
    expected = json.loads((package / 'package.json').read_text())
    compile(payload,'freedreno-native-run-001','exec')
    assert not out.exists()
    out.mkdir()
    prepare = "from pathlib import Path;p=Path('/home/zoinve/harmony-lab-freedreno-transfer-001');assert not p.exists();p.mkdir(mode=0o700)"
    r = subprocess.run(['ssh','-o','ConnectTimeout=3','matebook','python3 -'],input=prepare,text=True,capture_output=True,timeout=15)
    (out/'transfer-prepare.json').write_text(json.dumps(dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr),indent=2))
    r.check_returncode()
    subprocess.run(['scp',str(package/'bundle.tar.gz'),'matebook:/home/zoinve/harmony-lab-freedreno-transfer-001/bundle.tar.gz'],check=True,timeout=90)
    r = subprocess.run(['ssh','-o','ConnectTimeout=3','matebook','sudo -n python3 -'],
        input='expected='+repr(expected)+'\n'+payload,text=True,capture_output=True,timeout=170)
    (out/'remote.stdout').write_text(r.stdout,encoding='utf-8')
    (out/'remote.stderr').write_text(r.stderr,encoding='utf-8')
    r.check_returncode()
    report=json.loads(r.stdout)
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(gpu_pixel_test_passed=report['gpu_pixel_test_passed'],run=report['run'],
                         new_kernel_log=report['new_kernel_log'],desktop_verified=False),indent=2))
