"""A transport-only boot probe must preserve authentication and service identity."""
from pathlib import Path
import runpy
base=Path(__file__).resolve().parent
source=(base/'payload-917/init.c').read_text()
transform=runpy.run_path(str(base/'hdc-probe.py'))['hdc_probe']
result=transform(source)
assert 'setparam persist.hdc.mode.tcp enable' in result
assert 'hdc918-status' in result
assert 'param get const.security.developermode.state' in result
assert 'setparam const.security.developermode.state' not in result
assert 'setparam const.hdc.secure' not in result
assert 'setparam persist.hdc.daemon.auth' not in result
assert 'setuid(' not in result[len(source):]
assert transform(result)==result
print('PASS: transport probe does not disable authentication or forge developer state')
