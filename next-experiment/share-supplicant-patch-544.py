"""Keep the real MAGICLINK handshake on the official hostap2.12 API."""
from pathlib import Path

BASE=Path(__file__).resolve().parent
source=(BASE/'share-supplicant-patch-497.py').read_text()
old='d945ddd368085f255e68328f2d3b020ceea359af'
assert source.count(old)==1
source=source.replace(old,'831364bf02710ad09c2f27d3efa92abeeb5634c0',1)
old='request.frequency, 0, 0, 0, 0, 0, 0, NULL, 0, 1, false, 0, bssid);'
assert source.count(old)==1
source=source.replace(old,
    'request.frequency, 0, 0, 0, 0, 0, 0, NULL, 0, 1, false, 0, bssid,\n'
    '        NULL, NULL, NULL, 0, false, false);',1)
exec(compile(source,str(BASE/'share-supplicant-patch-544.generated.py'),'exec'),globals())
