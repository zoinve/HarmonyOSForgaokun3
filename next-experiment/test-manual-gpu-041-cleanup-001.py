"""No operational boot: prove the new archive retains the manual 032 init."""
from pathlib import Path
import runpy, subprocess
base = Path(__file__).resolve().parent
builder = base / 'build-manual-gpu-041-cleanup-001.py'
assert builder.exists(), 'missing manual GPU archive builder'
p = runpy.run_path(str(builder))
payload = p['verification']
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=payload, text=True, timeout=120).returncode)
