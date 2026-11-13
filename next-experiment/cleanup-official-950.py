"""Remove only completed 950 userdata after saved evidence and original guards."""
from pathlib import Path
import hashlib
import json
import subprocess

base = Path(__file__).resolve().parent
saved = base.parent / 'reports/official-arm-evidence-950'
evidence = {'offline-evidence/' + p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for p in saved.iterdir() if p.is_file()}
assert len(evidence) >= 5 and any(name.endswith('.zip') for name in evidence)
source = (base / 'cleanup-official-923.py').read_text().replace('full-system-923', 'full-system-950')
old = "evidence = old / 'readonly-cppcrash-1248-1794385026239.json'\nassert json.loads(evidence.read_text())['PNAME'] == '/system/bin/render_service'"
assert source.count(old) == 1
source = source.replace(old, "evidence = old / " + repr(next(iter(evidence))))
assert source.count('target.unlink()') == 1
source = source.replace('target.unlink()',
    f"for name, digest in {evidence!r}.items():\n    assert sha(old / name) == digest\ntarget.unlink()")
compile(source, 'cleanup-950', 'exec')
r = subprocess.run(['ssh', 'matebook', 'sudo -n python3 -'], input=source,
                   text=True, capture_output=True, check=True)
(base.parent / 'reports/userdata-cleanup-official-950.json').write_text(r.stdout)
print(r.stdout)
