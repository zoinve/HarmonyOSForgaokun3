"""Exact 2 GiB userdata cleanup with verified 951 evidence and original guards."""
from pathlib import Path
import hashlib
import json
import subprocess

base=Path(__file__).resolve().parent
saved=base.parent/'reports/official-arm-evidence-951-verified'
manifest=json.loads((saved/'evidence-manifest.json').read_text())
assert len(manifest)==8
for row in manifest:
    p=saved/row['name']
    assert p.stat().st_size==row['size'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
evidence={'offline-evidence-verified/'+p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in saved.iterdir() if p.is_file()}
source=(base/'cleanup-official-923.py').read_text().replace('full-system-923','full-system-951').replace('104857600','2147483648')
old="evidence = old / 'readonly-cppcrash-1248-1794385026239.json'\nassert json.loads(evidence.read_text())['PNAME'] == '/system/bin/render_service'"
assert source.count(old)==1
source=source.replace(old,"evidence = old / 'offline-evidence-verified/evidence-manifest.json'")
assert source.count('target.unlink()')==1
source=source.replace('target.unlink()',f"for name,digest in {evidence!r}.items():\n    assert sha(old/name)==digest\ntarget.unlink()")
compile(source,'cleanup-951','exec')
r=subprocess.run(['ssh','matebook','sudo -n python3 -'],input=source,text=True,capture_output=True,check=True)
(base.parent/'reports/userdata-cleanup-official-951.json').write_text(r.stdout)
print(r.stdout)
