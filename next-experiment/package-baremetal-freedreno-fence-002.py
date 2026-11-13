"""Re-use the exact proven fence probe; replace only the isolated Mesa library build."""
from pathlib import Path
import json
import runpy
import subprocess

base=Path(__file__).resolve().parent
reports=base.parent/'reports'
out=reports/'baremetal-freedreno-fence-package-002'
built=json.loads((reports/'baremetal-mesa-freedreno-build-003/result.json').read_text())
verified=json.loads((reports/'baremetal-mesa-freedreno-build-003/independent-verification.json').read_text())
assert built['build_success'] and verified['all_artifact_bytes_and_hashes_verified']
old=json.loads((reports/'baremetal-freedreno-fence-package-001/package.json').read_text())
new_hashes={row['path'].removeprefix('system/lib64/lab-freedreno003/'):row['sha256'] for row in built['artifacts']}
payload=runpy.run_path(str(base/'package-baremetal-freedreno-fence-001.py'))['payload']
for row in old['inputs']:
    prefix='/baremetal-mesa-freedreno-002/stage/system/lib64/lab-freedreno002/'
    if prefix in row['source']:
        name=row['source'].split(prefix,1)[1]
        assert row['sha256'] in payload,name
        payload=payload.replace(row['sha256'],new_hashes[name])
for before,after in [('baremetal-freedreno-fence-package-001','baremetal-freedreno-fence-package-002'),
                     ("work=root/'baremetal-freedreno-fence-001'","work=root/'baremetal-freedreno-fence-002'"),
                     ('baremetal-mesa-freedreno-002','baremetal-mesa-freedreno-003'),
                     ('lab-freedreno002','lab-freedreno003')]:
    assert before in payload,before
    payload=payload.replace(before,after)
anchor="r=subprocess.run(args,capture_output=True,text=True,timeout=60)\n(report/'compile.stdout').write_text(r.stdout);(report/'compile.stderr').write_text(r.stderr);r.check_returncode()"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"""prior=root/'baremetal-freedreno-fence-001'
assert (prior/'probe.c').read_text()==source
assert sha(prior/'bundle/probe')=='3f124cf9743ab84e0b8732853743cbe6130235e3dcbdd17e1810fb4bf069468e'
shutil.copyfile(prior/'bundle/probe',bundle/'probe');(bundle/'probe').chmod(0o555)
(report/'compile.stdout').write_text('Reused exact previously hardware-verified probe; no probe compilation performed.\\n')
(report/'compile.stderr').write_text('')""")
anchor='build_command=args,gpu_execution_verified=False'
assert payload.count(anchor)==1
payload=payload.replace(anchor,"probe_reused_unchanged=True,build_command_not_executed=args,gpu_execution_verified=False")
compile(payload,'fence-package002','exec')
if __name__=='__main__':
    regression=json.loads((reports/'baremetal-fd-identity-probe-004/result.json').read_text())
    assert regression['returncode']==0 and regression['actual_mesa_function_tested']
    assert not out.exists();out.mkdir()
    subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,check=True,timeout=120)
