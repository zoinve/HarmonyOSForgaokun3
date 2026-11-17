"""Extract sanitized library stack frames from the interrupted cumulative phase."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
source = (BASE / 'audit-interrupted-commercial-094.py').read_text()
source = source.replace('interrupted-run-audit.json', 'interrupted-run-stack-audit-v2.json')
old = "COMMERCIAL[0-9]+_|NATIVE_|EARLY093_|udidmodule|udid_static|udid_adp|GetDevUdid|SystemWriteParam"
new = "EVENT086_FILE_(?:BEGIN|END)|^Reason:|^Process name:|^#(?:00|01|02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20) pc|Js_GetTrustedDeviceListSync|libcollabfwk|libdevicepicker"
assert source.count(old) == 1
source = source.replace(old, new)
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
