"""Source contract only; not proof of target filter loading or a desktop."""
from pathlib import Path
import runpy
base=Path(__file__).resolve().parent
assert (base/'build-commercial-native-019.py').exists(),'missing narrow sandbox alias candidate'
p=runpy.run_path(str(base/'build-commercial-native-019.py'))
assert 'commercial61-original-001' in p['outer']
assert 'COMMERCIAL019' in p['outer'] and 'left033=210' in p['outer']
assert 'elapsed033<90' in p['outer'] and '8589934592' in p['outer']
assert '"/appdata-sandbox019.json"' in p['inner']
assert p['inner'].index('"/appdata-sandbox019.json"')<p['inner'].index('lowerdir=/system')
assert 'commercial-app-sandbox-019.py' in p['payload']
assert 'native-target/appdata-sandbox019.json' in p['payload']
assert 'char *const arguments[]={"/system/bin/init", "--second-stage",NULL};' in p['inner']
assert 'execve(arguments[0], arguments, environment);' in p['inner']
assert '--sandbox-switch on' not in p['inner'] # argv remains in original-derived launcher
assert 'libseccomp' not in p['inner']
print('PASS: original services, normal sandbox checks, one configuration alias and bounded return retained')
