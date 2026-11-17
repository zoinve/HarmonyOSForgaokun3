"""Replace only the old board-specific helper launchers in the RAM overlay."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-070.py'))
h = runpy.run_path(str(b / 'commercial-software-codec-072.py'))
inner = h['instrument'](p['inner'])
outer = p['outer'].replace('commercial61-native-070', 'commercial61-native-072').replace('COMMERCIAL070', 'COMMERCIAL072')
payload = p['payload'].replace('inner=' + repr(p['inner']), 'inner=' + repr(inner), 1).replace(
    'outer=' + repr(p['outer']), 'outer=' + repr(outer), 1)
payload = payload.replace('commercial61-native-070', 'commercial61-native-072')
anchor = 'def member(name,mode,data,ino):'
assert payload.count(anchor) == 1
addition = """
codec072=runpy.run_path(str(base/'commercial-software-codec-072.py'))
entries,added072=codec072['add_entries'](entries)
provenance072=dict(files=[dict(name=n,mode=oct(m),bytes=len(d),sha256=hashlib.sha256(d).hexdigest()) for n,(m,d) in sorted(added072.items())],
 ram_only=True,system_overlay_readonly=True,original_init_service_definitions_unchanged=True,
 original_codec_adapters_unchanged=True,peer_uid=1013,source_images_written=False,
 original_authentication_changed=False,private_abi_interposed=False,desktop_verified=False)
(local/'software-codec-provenance.json').open('x').write(json.dumps(provenance072,indent=2))
"""
payload = payload.replace(anchor, addition + '\n' + anchor, 1)
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
