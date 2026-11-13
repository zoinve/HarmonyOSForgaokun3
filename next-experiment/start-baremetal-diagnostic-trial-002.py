"""Correct persistent-default verification; preserve the refused first request."""
from pathlib import Path

base = Path(__file__).resolve().parent
source = (base / 'start-baremetal-diagnostic-trial-001.py').read_text()
old = "assert next(e for e in entries if e['isDefault'])['id']=='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'"
new = "assert (var/('LoaderEntryDefault-'+guid)).read_bytes()[4:].decode('utf-16-le').rstrip('\\0')=='8a29534fa802480d9fbb71aa18c01d7b-7.1.0-rc3-gaokun3+.conf'"
assert source.count(old) == 1
source = source.replace(old, new)
source = source.replace('baremetal-diagnostic-trial-001-start', 'baremetal-diagnostic-trial-001-start-002')
exec(compile(source, str(base / 'start-baremetal-diagnostic-trial-002.py'), 'exec'))
