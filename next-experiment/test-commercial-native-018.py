"""Offline archive/source gates; no installation or device access."""
from pathlib import Path
import runpy
base=Path(__file__).resolve().parent
builder=base/'build-commercial-native-018.py'
assert builder.is_file(),'missing original-AppSpawn board launcher integration'
p=runpy.run_path(str(builder))
assert 'commercial61-native-018-%s' in p['outer']
assert 'left033=210' in p['outer'] and 'elapsed033<90' in p['outer']
assert "commercial_copy005(\"/graphics016/system/bin/l410_launch_appspawn_r18_namespace.sh\"" in p['inner']
assert "commercial-appspawn-018.py" in p['payload']
assert p['payload'].index("entries[key]=")<p['payload'].index("['complete'](entries)")
assert 'commercial61-original-001' in p['outer']
assert 'sdk_payload=0' in p['inner']
print('PASS: original AppSpawn launcher added before read-only overlay; immutable commercial images and bounded return retained')
