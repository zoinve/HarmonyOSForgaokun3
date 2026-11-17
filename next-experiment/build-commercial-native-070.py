"""Test stock HAP-adjacent rawfile resolution without private ABI hooks."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-069.py'))
h = runpy.run_path(str(b / 'commercial-original-resources-070.py'))
hap = b.parent / 'reports/commercial-ui-resources-audit-068/HwStartupGuide.hap'
files = h['rawfiles'](hap.read_bytes())
assert len(files) == 46 and sum(map(len, files.values())) == 6402165
inner = h['instrument'](p['inner'], files)
outer = p['outer'].replace('commercial61-native-069', 'commercial61-native-070').replace('COMMERCIAL069', 'COMMERCIAL070')
payload = p['payload'].replace('inner='+repr(p['inner']), 'inner='+repr(inner), 1).replace(
    'outer='+repr(p['outer']), 'outer='+repr(outer), 1)
payload = payload.replace('commercial61-native-069', 'commercial61-native-070')
anchor = 'def member(name,mode,data,ino):'
assert payload.count(anchor) == 1
addition = """
resource070=runpy.run_path(str(base/'commercial-original-resources-070.py'))
original070=(base.parent/'reports/commercial-ui-resources-audit-068/HwStartupGuide.hap').read_bytes()
files070=resource070['rawfiles'](original070)
entries,added070=resource070['add_entries'](entries,files070)
provenance070=dict(original_hap_sha256=resource070['HAP_SHA256'],
 files=[dict(name=n,bytes=len(d),sha256=hashlib.sha256(d).hexdigest()) for n,d in sorted(files070.items())],
 archive_members=sorted(added070),ram_only=True,system_overlay_readonly=True,
 original_images_written=False,installed_records_modified=False,private_abi_interposed=False,
 runtime_resolution_verified=False,desktop_verified=False)
(local/'original-resources-provenance.json').open('x').write(json.dumps(provenance070,indent=2))
"""
payload = 'import runpy\n' + payload.replace(anchor, addition+'\n'+anchor, 1)
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
