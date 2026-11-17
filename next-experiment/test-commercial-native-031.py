"""Only diagnostic provider and run identifier change from closed 030."""
from pathlib import Path
import runpy
b=Path(__file__).resolve().parent
assert (b/'build-commercial-native-031.py').exists(),'missing pixel-boundary candidate'
p=runpy.run_path(str(b/'build-commercial-native-031.py'))
assert p['inner']==p['p']['inner']
assert 'commercial-egl-031/result.json' in p['payload']
assert 'commercial-composer-030/result.json' in p['payload']
assert 'commercial61-native-031-%s' in p['outer']
assert 'left033=210' in p['outer'] and 'elapsed033<90' in p['outer']
assert "work=root/'commercial61-native-031';" in p['payload']
print('PASS: original bootstrap, fresh composer observations and bounded diagnostic guards retained')
