"""Repeat the same private pixel probe, capturing unit policy before transient-unit GC."""
from pathlib import Path
import json
import runpy
import subprocess

base=Path(__file__).resolve().parent.parent
package=base/'reports/baremetal-freedreno-probe-package-001'
out=base/'reports/baremetal-freedreno-probe-run-002'
source=runpy.run_path(str(base/'next-experiment/run-baremetal-freedreno-probe-001.py'),run_name='payload_only')['payload']
start=source.index("raw=Path('/home/zoinve/harmony-lab-freedreno-transfer-001/bundle.tar.gz')")
end=source.index("props=['User=zoinve'",start)
source=source[:start]+r'''
stage=Path('/var/lib/harmony-lab-freedreno-probe-001');assert stage.is_dir()
files={r['path']:r for r in expected['files']};links=expected['symlinks']
for name,row in files.items():
    p=stage/name;assert not p.is_symlink() and p.stat().st_size==row['bytes'] and sha(p.read_bytes())==row['sha256'],name
for name,target in links.items():assert (stage/name).is_symlink() and os.readlink(stage/name)==target
'''+source[end:]
source=source.replace("def service(unit,args):",r'''
capture=['LoadState','Transient','User','SupplementaryGroups','DevicePolicy','DeviceAllow',
         'NoNewPrivileges','CapabilityBoundingSet','ProtectSystem','ProtectHome','PrivateNetwork',
         'PrivateTmp','RestrictAddressFamilies','RuntimeMaxUSec','MemoryMax','TasksMax']
props.append('ExecStartPre=/usr/bin/systemctl show '+' '.join('--property='+p for p in capture)+' %n')
def service(unit,args):''')
source=source.replace('harmony-lab-freedreno-sandbox-001','harmony-lab-freedreno-sandbox-002')
source=source.replace('harmony-lab-freedreno-probe-001.service','harmony-lab-freedreno-probe-002.service')
source=source.replace("service('harmony-lab-freedreno-probe-001'", "service('harmony-lab-freedreno-probe-002'")
source=source.replace("assert sandbox['returncode']==0,sandbox",r'''
assert sandbox['returncode']==0,sandbox
def policy_observed(output):
    pairs=dict(line.split('=',1) for line in output.splitlines() if '=' in line)
    assert pairs.get('LoadState')=='loaded' and pairs.get('Transient')=='yes',pairs
    assert pairs.get('User')=='zoinve' and pairs.get('DevicePolicy')=='closed',pairs
    assert pairs.get('NoNewPrivileges')=='yes' and pairs.get('CapabilityBoundingSet')=='',pairs
    assert pairs.get('ProtectSystem')=='strict' and pairs.get('ProtectHome')=='yes',pairs
    assert pairs.get('PrivateNetwork')=='yes' and pairs.get('PrivateTmp')=='yes',pairs
    assert pairs.get('SupplementaryGroups')=='render',pairs
    assert pairs.get('DeviceAllow')=='/dev/dri/renderD128 rw',pairs
    return pairs
sandbox_policy=policy_observed(sandbox['stdout'])
''')
source=source.replace("effective_service_properties=properties,new_kernel_log=new_kernel,",
    "effective_service_properties_before_probe=policy_observed(result['stdout']),sandbox_effective_policy=sandbox_policy,\n lifecycle_query_after_exit=properties,new_kernel_log=new_kernel,")
compile(source,'native-freedreno-run-002','exec')

if __name__=='__main__':
    assert not out.exists();out.mkdir()
    expected=json.loads((package/'package.json').read_text())
    r=subprocess.run(['ssh','-o','ConnectTimeout=3','matebook','sudo -n python3 -'],
        input='expected='+repr(expected)+'\n'+source,text=True,capture_output=True,timeout=170)
    (out/'remote.stdout').write_text(r.stdout,encoding='utf-8')
    (out/'remote.stderr').write_text(r.stderr,encoding='utf-8')
    r.check_returncode();report=json.loads(r.stdout)
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(gpu_pixel_test_passed=report['gpu_pixel_test_passed'],stdout=report['run']['stdout'],
                         effective_policy=report['effective_service_properties_before_probe'],
                         new_kernel_log=report['new_kernel_log'],desktop_verified=False),indent=2))
