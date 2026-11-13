"""Fresh audit of build 002; preserve failed audit 002 and use its actual manifest."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('verify-original-adreno-mesa-002.py')))['payload']
payload = payload.replace('reports/original-adreno-mesa-002-independent', 'reports/original-adreno-mesa-003-independent')
old = """manifest = work/'result.json'
d = json.loads(manifest.read_text())
assert json.loads((project/'reports/original-adreno-mesa-002/result.json').read_text()) == d"""
assert payload.count(old) == 1
payload = payload.replace(old, """manifest = project/'reports/original-adreno-mesa-002/result.json'
d = json.loads(manifest.read_text())""")
compile(payload, 'independent-adreno-audit003', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],
                                   input=payload,text=True,timeout=240).returncode)
