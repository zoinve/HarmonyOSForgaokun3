from pathlib import Path
import runpy
base=Path(__file__).resolve().parent
assert (base/'build-commercial-native-023.py').is_file(),'missing native mapper visibility candidate'
p=runpy.run_path(str(base/'build-commercial-native-023.py'))
for name in ['libEGL_impl.so','libGLESv1_impl.so','libGLESv2_impl.so','libGLESv3_impl.so']:
    assert f'/run/commercial-vendor004/upper/lib64/passthrough/{name}' in p['inner']
    assert f'/graphics016/system/lib64/{name}' in p['inner']
assert p['inner'].index('commercial_vendor016();')<p['inner'].index('const char *options="lowerdir=/vendor')
assert 'commercial-mapper-path-023.py' in p['payload']
assert 'commercial61-original-001' in p['outer']
assert 'commercial61-native-023-%s' in p['outer']
assert 'elapsed033<90' in p['outer'] and 'left033=210' in p['outer']
print('PASS: original mapper preserved; own GPU implementations only; original service identities and bounded boot retained')
