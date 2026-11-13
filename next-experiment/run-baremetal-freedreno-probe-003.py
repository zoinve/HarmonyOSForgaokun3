"""Capture live transient-unit policy with a literal unit name, then repeat the pixel test."""
from pathlib import Path
import json
import runpy
import subprocess

base=Path(__file__).resolve().parent.parent
out=base/'reports/baremetal-freedreno-probe-run-003'
package=base/'reports/baremetal-freedreno-probe-package-001'
source=runpy.run_path(str(base/'next-experiment/run-baremetal-freedreno-probe-002.py'),run_name='payload_only')['source']
source=source.replace('harmony-lab-freedreno-sandbox-002','harmony-lab-freedreno-sandbox-003')
source=source.replace('harmony-lab-freedreno-probe-002','harmony-lab-freedreno-probe-003')
anchor="for p in props:cmd+=['--property='+p]"
assert source.count(anchor)==1
source=source.replace(anchor,"for p in props:cmd+=['--property='+p.replace('%n',unit+'.service')]")
compile(source,'native-freedreno-run-003','exec')

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
