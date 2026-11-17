from pathlib import Path
import runpy
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-commercial-native-022.py'))
assert p['inner']==p['p']['inner'], 'no bootstrap/service identity change required'
assert 'commercial61-original-001' in p['outer']
assert 'left033=210' in p['outer'] and 'elapsed033<90' in p['outer']
assert "base/'commercial-sceneboard-mounts-022.py'" in p['payload']
assert 'commercial-app-sandbox-019.py' in p['payload']
assert 'commercial-desktop-order-021.py' in p['payload']
assert 'commercial61-native-022-%s' in p['outer']
print('PASS: only sandbox mount sources and unique run identifier change; original services/bounds retained')
