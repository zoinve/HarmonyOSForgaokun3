"""Fresh offline 009: native profile003 plus QEMU047-tested legacy/enforcing read helper."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
parent=runpy.run_path(str(base/'prepare-baremetal-diagnostic-init-008.py'))
source=runpy.run_path(str(base/'baremetal-diagnostic-native-identity-009.py'))['build_source'](parent['source'])
old=parent['payload'];start=old.index('\nfrom pathlib import Path')+1
payload='source='+repr(source)+'\n'+old[start:]
old_block="""checked=json.loads((root/'baremetal-identity-qemu-009/result.json').read_text());assert checked['runtime_verified'] and checked['diagnostic_read_probe_verified']
helper=root/'baremetal-identity-native-read-009/sdk/native-probe'
assert (helper.parent.parent/'native-probe.c').read_bytes()==(base/'baremetal-native-identity-read-001.c').read_bytes()
meta=json.loads((root/'baremetal-identity-native-read-009/result.json').read_text());row=next(r for r in meta['ram_files'] if r['name']=='sdk/native-probe');assert sha(helper)==row['sha256'] and helper.stat().st_size==row['bytes']"""
new_block="""checked=json.loads((root/'baremetal-native-identity-qemu-047/result.json').read_text());assert checked['runtime_verified'] and len(checked['cases'])==2 and all(case['verified'] for case in checked['cases'])
audit=json.loads((project/'reports/baremetal-native-identity-qemu-047/independent-verification.json').read_text());assert audit['positive_legacy_binder_and_enforcing_verified'] and audit['missing_opt_in_refused']
helper=root/'baremetal-native-identity-qemu-047/probe'
assert (helper.parent/'baremetal-native-identity-read-002.c').read_bytes()==(base/'baremetal-native-identity-read-002.c').read_bytes()
row=checked['files']['probe'];assert sha(helper)==row['sha256'] and helper.stat().st_size==row['bytes']"""
assert payload.count(old_block)==1
payload=payload.replace(old_block,new_block)
for old,new in [('baremetal-diagnostic-init-008','baremetal-diagnostic-init-009'),('baremetal-identity-native-package-001','baremetal-identity-native-package-002'),('bin/native-identity-read-001','bin/native-identity-read-002')]:
    assert old in payload,old
    payload=payload.replace(old,new)
compile(payload,'native-diagnostic-009-preparation','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=150)
    raise SystemExit(r.returncode)
