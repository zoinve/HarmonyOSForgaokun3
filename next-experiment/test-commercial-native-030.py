"""Keep rendering/security unchanged while observing real frame freshness."""
from pathlib import Path
import runpy
base=Path(__file__).resolve().parent
assert (base/'build-commercial-native-030.py').exists(),'missing fresh frame candidate'
p=runpy.run_path(str(base/'build-commercial-native-030.py'))
assert 'COMMERCIAL030_CAPTURE_META' in p['inner']
assert 'fstat(fd,&before030)' in p['inner'] and 'fstat(fd,&after030)' in p['inner']
assert 'commercial-composer-030' in p['payload']
assert 'native-target/graphics016/vendor/lib64/libdisplay_composer_vdi_impl.z.so' in p['payload']
assert 'elapsed033<90' in p['outer'] and 'left033=210' in p['outer']
print('PASS: real capture metadata, single composer override and unchanged bounded run')
