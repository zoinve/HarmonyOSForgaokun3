"""Exact 944 userdata cleanup after all saved offline evidence is verified."""
from pathlib import Path
import hashlib
import json
import subprocess

base = Path(__file__).resolve().parent
reports = base.parent / 'reports'
saved = reports / 'official-arm-evidence-944'
crashes = sorted(saved.glob('cppcrash-*.json'))
assert len(crashes) == 4
assert all(json.loads(p.read_text())['PNAME'] == '/system/bin/render_service' for p in crashes)
evidence = {'offline-evidence/' + p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in saved.iterdir() if p.is_file()}
assert len(evidence) >= 8
source = (base / 'cleanup-official-923.py').read_text().replace('full-system-923', 'full-system-944')
old = "evidence = old / 'readonly-cppcrash-1248-1794385026239.json'"
assert source.count(old) == 1
source = source.replace(old, "evidence = old / 'offline-evidence/" + crashes[0].name + "'")
assert source.count('target.unlink()') == 1
source = source.replace('target.unlink()',
    f"for name, digest in {evidence!r}.items():\n    assert sha(old / name) == digest\ntarget.unlink()")
compile(source, 'cleanup-944-guarded', 'exec')
r = subprocess.run(['ssh', 'matebook', 'sudo -n python3 -'], input=source,
                   text=True, capture_output=True, check=True)
(reports / 'userdata-cleanup-official-944.json').write_text(r.stdout)
print(r.stdout)
