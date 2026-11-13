"""Inspect original first-stage init too; retain prior numbered audit unchanged."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('audit-baremetal-sdk-init-bootstrap-001.py')))['payload']
old="base in ('init','libload_policy.z.so')"
assert payload.count(old)==1
payload=payload.replace(old,"base in ('init_early','libload_policy.z.so')")
payload=payload.replace('baremetal-sdk-init-bootstrap-001','baremetal-sdk-init-bootstrap-002')
payload=payload.replace("bootstrap_entries=result['bootstrap_entries'],", "bootstrap_entries={k:v for k,v in result['bootstrap_entries'].items() if '/' not in k or 'init' in k},")
compile(payload,'sdk-init-bootstrap-002-audit','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=60)
    raise SystemExit(r.returncode)
