"""Same proven fence executable and live-captured render-only sandbox, new Mesa libraries."""
from pathlib import Path
import json
import runpy
import subprocess

base=Path(__file__).resolve().parent.parent
package=base/'reports/baremetal-freedreno-fence-package-002'
out=base/'reports/baremetal-freedreno-fence-run-002'
source=runpy.run_path(str(base/'next-experiment/run-baremetal-freedreno-fence-001.py'),run_name='payload_only')['source']
for old,new in [('harmony-lab-freedreno-fence-001','harmony-lab-freedreno-fence-002'),
                ('harmony-lab-freedreno-fence-transfer-001','harmony-lab-freedreno-fence-transfer-002'),
                ('harmony-lab-freedreno-fence-sandbox-001','harmony-lab-freedreno-fence-sandbox-002'),
                ('harmony-lab-freedreno-fence-probe-001','harmony-lab-freedreno-fence-probe-002')]:
    assert old in source,old
    source=source.replace(old,new)
# Preserve all original extraction, FD admission, live policy and asset preservation checks.
compile(source,'fence-run002-remote','exec')
if __name__=='__main__':
    expected=json.loads((package/'package.json').read_text())
    assert expected['probe_reused_unchanged'] and next(row for row in expected['files'] if row['path']=='probe')['sha256']=='3f124cf9743ab84e0b8732853743cbe6130235e3dcbdd17e1810fb4bf069468e'
    assert not out.exists();out.mkdir()
    prepare="from pathlib import Path;p=Path('/home/zoinve/harmony-lab-freedreno-fence-transfer-002');assert not p.exists();p.mkdir(mode=0o700)"
    r=subprocess.run(['ssh','-o','ConnectTimeout=3','matebook','python3 -'],input=prepare,text=True,capture_output=True,timeout=15)
    (out/'transfer-prepare.json').write_text(json.dumps(dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr),indent=2))
    r.check_returncode()
    subprocess.run(['scp',str(package/'bundle.tar.gz'),'matebook:/home/zoinve/harmony-lab-freedreno-fence-transfer-002/bundle.tar.gz'],check=True,timeout=90)
    r=subprocess.run(['ssh','-o','ConnectTimeout=3','matebook','sudo -n python3 -'],input='expected='+repr(expected)+'\n'+source,text=True,capture_output=True,timeout=170)
    (out/'remote.stdout').write_text(r.stdout,encoding='utf-8');(out/'remote.stderr').write_text(r.stderr,encoding='utf-8')
    r.check_returncode();report=json.loads(r.stdout)
    warning='os_same_file_description' in report['run']['stderr']
    report['same_probe_executable_reused']=True
    report['fd_identity_warning_present']=warning
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(gpu_pixel_test_passed=report['gpu_pixel_test_passed'],stdout=report['run']['stdout'],stderr=report['run']['stderr'],fd_identity_warning_present=warning,returncode=report['run']['returncode'],new_kernel_log=report['new_kernel_log']),indent=2))
