"""Narrow sanitized partial-run audit without replacing the initial inventory."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
source = (BASE / 'audit-interrupted-commercial-094.py').read_text()
source = source.replace('interrupted-run-audit.json', 'interrupted-run-focused-audit.json')
old = "COMMERCIAL[0-9]+_|NATIVE_|EARLY093_|udidmodule|udid_static|udid_adp|GetDevUdid|SystemWriteParam"
new = "EARLY093_|HARDWARE091_|PRIVACY093_|udidmodule|udid_static|udid_adp|GetDevUdid|SystemWriteParam|COMMERCIAL[0-9]+_.*(?:OOBE|EXIT|DESKTOP|IDENTITY)|THREAD_BLOCK|sessionExceptionCallback"
assert source.count(old) == 1
source = source.replace(old, new)
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
