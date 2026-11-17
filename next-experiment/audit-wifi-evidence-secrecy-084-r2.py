"""Also inspect overlapping hex windows; preserve the initial audit result."""
from pathlib import Path
import re

b = Path(__file__).resolve().parent
source = (b / 'audit-wifi-evidence-secrecy-084.py').read_text()
old = "re.compile(rb'[0-9a-fA-F]{64}')"
new = "re.compile(rb'(?=([0-9a-fA-F]{64}))')"
assert source.count(old) == 1
source = source.replace(old, new, 1).replace('match.group().lower()', 'match.group(1).lower()')
source = source.replace('evidence-secrecy-audit.json', 'evidence-secrecy-audit-revision2.json')
source = source.replace("result.update(files_scanned=", "result.update(overlapping_hex_windows_scanned=True, files_scanned=")
token = b'0123456789abcdef' * 4
assert token in [match.group(1) for match in re.compile(rb'(?=([0-9a-fA-F]{64}))').finditer(b'a' + token + b'b')]

if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
