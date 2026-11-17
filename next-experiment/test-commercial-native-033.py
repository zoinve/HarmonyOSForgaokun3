"""Constrain 033 to dispatch observations without changing the boot or launcher."""
from pathlib import Path
import runpy
b=Path(__file__).resolve().parent
assert (b/'build-commercial-native-033.py').exists(),'missing dispatch observation candidate'
p=runpy.run_path(str(b/'build-commercial-native-033.py'))
assert p['inner']==p['p']['inner']
assert 'commercial-egl-033/result.json' in p['payload']
assert 'commercial-composer-030/result.json' in p['payload']
assert "base/'commercial-desktop-retry-032.py'" in p['payload']
assert 'commercial61-native-033-%s' in p['outer']
assert 'elapsed033<90' in p['outer'] and 'left033=210' in p['outer']
print('PASS: same original bootstrap/launcher/composer and bounded deadlines; own EGL observations only')
