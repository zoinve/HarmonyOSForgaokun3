"""Run new Mesa003's real compiled comparator under the same rootless OHOS conditions."""
from pathlib import Path
import json
import runpy

base=Path(__file__).resolve().parent.parent
source=runpy.run_path(str(Path(__file__).with_name('run-baremetal-fd-identity-probe-003.py')))['source']
for old,new in [('baremetal-fd-identity-probe-003','baremetal-fd-identity-probe-004'),
                ('fd-identity-transfer-003','fd-identity-transfer-004'),
                ('harmony-lab-fd-identity-probe-003','harmony-lab-fd-identity-probe-004'),
                ('FD_IDENTITY003','FD_IDENTITY004'),
                ('baremetal-mesa-freedreno-002','baremetal-mesa-freedreno-003')]:
    assert old in source,old
    source=source.replace(old,new)
anchor='gpu_tested=False,reboot_requested=False,security_permissions_relaxed=False'
assert source.count(anchor)==1
source=source.replace(anchor,'actual_mesa_function_tested=True,'+anchor)
compile(source,'fd-identity004-new-mesa','exec')
if __name__=='__main__':
    failed=json.loads((base/'reports/baremetal-fd-identity-probe-003/result.json').read_text())
    assert failed['returncode']==1 and 'kcmp_duplicate=-1 errno=0 kcmp_independent=-1 errno=0' in failed['stdout']
    built=json.loads((base/'reports/baremetal-mesa-freedreno-build-003/result.json').read_text())
    assert built['build_success'] and built['previous_build_002_verified_unchanged'] and built['allow_kcmp_explicitly_enabled']
    exec(compile(source,__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})
