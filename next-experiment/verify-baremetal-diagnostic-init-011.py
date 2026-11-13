"""Independent full-record comparison: 011 differs from 010 in exactly five Mesa libraries."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('verify-baremetal-diagnostic-init-010.py')))['payload']
payload=payload.replace('baremetal-diagnostic-init-010','baremetal-diagnostic-init-011')
payload=payload.replace('baremetal-freedreno-fence-package-001','baremetal-freedreno-fence-package-002')
anchor="out.write_text(json.dumps(result,indent=2)+'\\n');"
assert payload.count(anchor)==1
extra=r'''
previous_meta=json.loads((project/'reports/baremetal-diagnostic-init-010/result.json').read_text())
previous_path=Path(previous_meta['archive'])
assert sha(previous_path)==previous_meta['archive_sha256']
previous=archive(previous_path)
assert previous.keys()==new.keys()
changed=sorted(name for name in previous if previous[name]!=new[name])
expected=sorted('opt/native-mesa-001/lib/'+name for name in
 ['libEGL.so.1','libGLESv2.so.2','libgbm.so.1','libgallium-25.0.1.so','gbm/dri_gbm.so'])
assert changed==expected,changed
assert new['init']==previous['init'] and new['bin/native-mesa-launcher-001']==previous['bin/native-mesa-launcher-001']
result.update(only_five_mesa_libraries_changed=True,changed_archive_entries=changed,
              all_other_010_records_unchanged=True,native_gpu_execution_verified=False)
'''
payload=payload.replace(anchor,extra+'\n'+anchor)
compile(payload,'independent-diag011','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120)
    raise SystemExit(r.returncode)
