"""Reference helpers must be deployed into the actual volatile system overlay."""
from pathlib import Path
import runpy
b=Path(__file__).resolve().parent
assert (b/'build-commercial-native-036.py').exists(),'missing reference-based candidate'
p=runpy.run_path(str(b/'build-commercial-native-036.py'))
for name in ['samgr-service-probe','appspawn-reference-namespace']:
 assert f'/graphics016/system/bin/aurora/{name}' in p['inner']
 assert f'/run/commercial-system005/upper/bin/aurora/{name}' in p['inner']
assert 'commercial-desktop-retry-032.py' not in p['payload']
assert 'commercial-reference-start-036.py' in p['payload']
assert 'commercial-reference-namespace-036.py' in p['payload']
assert 'elapsed033<90' in p['outer'] and 'left033=210' in p['outer']
compile(p['payload'],'<036>','exec')
print('PASS: reference gate/namespace integrated, real helper paths and return guards retained')
