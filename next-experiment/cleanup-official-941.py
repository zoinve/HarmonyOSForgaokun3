"""Delete only completed 941 userdata after verifying preserved evidence."""
from pathlib import Path
import hashlib
import json
import subprocess

base = Path(__file__).resolve().parent
reports = base.parent / 'reports'
evidence = {}
for p in sorted((reports / 'official-arm-crashes-941').glob('cppcrash-*.json')):
    assert json.loads(p.read_text())['PNAME'] == '/system/bin/render_service'
    evidence['crash-evidence/' + p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
assert len(evidence) == 4
for name in ['hilog.000.20261111-175423.gz', 'hilog_dict.20261111-175428.zip', '.dict_info.json']:
    p = reports / 'official-arm-hilog-941' / name
    evidence['hilog-evidence/' + name] = hashlib.sha256(p.read_bytes()).hexdigest()
source = (base / 'cleanup-official-923.py').read_text()
source = source.replace('full-system-923', 'full-system-941')
old = "evidence = old / 'readonly-cppcrash-1248-1794385026239.json'"
assert source.count(old) == 1
source = source.replace(old, "evidence = old / 'crash-evidence/cppcrash-657-1794390866022.json'")
anchor = 'target.unlink()'
assert source.count(anchor) == 1
source = source.replace(anchor, f"for name, digest in {evidence!r}.items():\n    assert sha(old / name) == digest\n" + anchor)
compile(source, 'cleanup-941-guarded', 'exec')
r = subprocess.run(['ssh', 'matebook', 'sudo -n python3 -'], input=source,
                   text=True, capture_output=True, check=True)
(reports / 'userdata-cleanup-official-941.json').write_text(r.stdout)
print(r.stdout)
