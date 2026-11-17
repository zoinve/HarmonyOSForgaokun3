"""Retain real software backend and observe public allocator/service boundaries."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-072.py'))
h = runpy.run_path(str(b / 'commercial-allocator-observer-073.py'))
inner = h['inner'](p['inner'])
outer = p['outer'].replace('commercial61-native-072', 'commercial61-native-073').replace('COMMERCIAL072', 'COMMERCIAL073')
payload = p['payload'].replace('inner=' + repr(p['inner']), 'inner=' + repr(inner), 1).replace(
    'outer=' + repr(p['outer']), 'outer=' + repr(outer), 1)
payload = payload.replace('commercial61-native-072', 'commercial61-native-073')
anchor = 'def member(name,mode,data,ino):'
assert payload.count(anchor) == 1
addition = """
allocator073=root/'commercial-allocator-073'
provenance073=json.loads((allocator073/'result.json').read_text())
library073=(allocator073/'libdisplay_buffer_vdi_impl.z.so').read_bytes()
assert hashlib.sha256(library073).hexdigest()==provenance073['sha256']
assert provenance073['exact_public_logging_only'] and provenance073['allocator_return_values_unchanged']
assert 'native-target/allocator073' not in entries
entries['native-target/allocator073']=(stat.S_IFDIR|0o755,b'')
entries['native-target/allocator073/libdisplay_buffer_vdi_impl.z.so']=(stat.S_IFREG|0o755,library073)
(local/'allocator-provenance.json').open('x').write(json.dumps(provenance073,indent=2))
"""
payload = payload.replace(anchor, addition + '\n' + anchor, 1)
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
