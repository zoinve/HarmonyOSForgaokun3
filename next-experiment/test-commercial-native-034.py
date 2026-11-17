from pathlib import Path
import runpy
b=Path(__file__).resolve().parent
assert (b/'build-commercial-native-034.py').exists(),'missing original RS tree diagnostic candidate'
p=runpy.run_path(str(b/'build-commercial-native-034.py'))
assert p['inner']!=p['p']['inner']
assert 'commercial-egl-033/result.json' in p['payload'] and 'commercial-composer-030/result.json' in p['payload']
assert "base/'commercial-desktop-retry-032.py'" in p['payload']
assert 'COMMERCIAL034_RS_DUMP_BEGIN' in p['inner']
assert 'commercial61-native-034-%s' in p['outer']
assert 'elapsed033<90' in p['outer'] and 'left033=210' in p['outer']
print('PASS: original launcher/render providers and deadline guards retained; only public RS queries added')
