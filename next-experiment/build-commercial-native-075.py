"""Use the pinned reference guide dismissal, preserving real activation failure."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-074.py'))
h = runpy.run_path(str(b / 'commercial-desktop-evidence-075.py'))
inner, outer = h['inner'](p['inner']), h['outer'](p['outer'])
payload = p['payload'].replace('inner=' + repr(p['inner']), 'inner=' + repr(inner), 1).replace(
    'outer=' + repr(p['outer']), 'outer=' + repr(outer), 1).replace('commercial61-native-074', 'commercial61-native-075')
anchor = 'def member(name,mode,data,ino):'
addition = '''
key075='native-target/commercial-direct-desktop-075.sh'
script075=(base/'commercial-direct-desktop-075.sh').read_bytes()
assert key075 not in entries
entries[key075]=(stat.S_IFREG|0o755,script075)
composer075=root/'commercial-composer-075'
record075=json.loads((composer075/'result.json').read_text())
binary075=(composer075/'libdisplay_composer_vdi_impl.z.so').read_bytes()
assert hashlib.sha256(binary075).hexdigest()==record075['composer_sha256']
key075='native-target/graphics016/vendor/lib64/libdisplay_composer_vdi_impl.z.so'
entries[key075]=(entries[key075][0],binary075)
(local/'second-capture-provenance.json').open('x').write(json.dumps(record075,indent=2))
(local/'direct-desktop075.sh').open('xb').write(script075)
'''
assert payload.count(anchor) == 1
payload = payload.replace(anchor, addition + '\n' + anchor, 1)
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
