from pathlib import Path
import runpy
base=Path(__file__).resolve().parent
assert (base/'build-commercial-native-032.py').is_file(),'missing late-BMS candidate'
p=runpy.run_path(str(base/'build-commercial-native-032.py'))
assert p['inner']==p['p']['inner']
assert 'commercial-egl-031' in p['payload'] and 'commercial-composer-030' in p['payload']
assert "base/'commercial-desktop-retry-032.py'" in p['payload']
assert 'commercial61-native-032-%s' in p['outer']
assert 'elapsed033<90' in p['outer'] and 'left033=210' in p['outer']
print('PASS: bounded launcher retry only; rendering providers/bootstrap/deadlines unchanged')
