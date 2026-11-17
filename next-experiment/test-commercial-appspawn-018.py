"""Keep actual original appspawn argv; replace only Kirin hardware wrapping."""
from pathlib import Path
import runpy,shlex
base=Path(__file__).resolve().parent
repair=base/'commercial-appspawn-018.py'
assert repair.is_file(),'missing MateBook appspawn hardware-launcher adaptation'
p=runpy.run_path(str(repair))
original="#!/system/bin/sh\nset -eu\nexec /system/bin/l410_appspawn_r18_namespace_exec /data/local/tmp/l410-sceneboard-r18-passthrough-v2 /system/bin/appspawn '-mode appspawn' '--sandbox-switch on --process-name com.ohos.appspawn.startup --type standard '\n"
actual=p['repair'](original)
assert p['repair'](original.replace(' /data/',' \\\n /data/'))==actual
assert shlex.split(actual.split('exec ',1)[1])==shlex.split(original.split('exec ',1)[1])[2:]
assert 'passthrough' not in actual and 'LD_PRELOAD' not in actual
assert not any(x in actual for x in ['setuid','setgid','sandbox-switch off','sysctl','chmod'])
try:p['repair'](actual)
except AssertionError:pass
else:raise AssertionError('already-adapted launcher must be rejected')
print('PASS original appspawn argv retained; Kirin-only wrapper removed, no identity or sandbox-option changes')
