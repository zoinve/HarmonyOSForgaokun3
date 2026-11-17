"""Test the original public full-render configuration in an isolated initrd."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-052.py'))
inner = p['inner']
outer = runpy.run_path(str(b / 'commercial-hwbreak-059.py'))['instrument'](p['outer'])
outer = outer.replace('commercial61-native-052', 'commercial61-native-059').replace('COMMERCIAL052', 'COMMERCIAL059')
payload = p['payload'].replace('outer=' + repr(p['outer']), 'outer=' + repr(outer), 1)
payload = payload.replace('commercial61-native-052', 'commercial61-native-059')
extra = r'''
audit=json.loads((local.parent/'commercial-partial-render-audit-059/result.json').read_text())
assert audit['original_binary_hashes_verified'] and audit['selected_value']==0
key='native-target/graphics016/sys_prod/etc/param/hw_defaults.para'
mode,before=entries[key]
assert b'rosen.uni.partialrender.enabled' not in before
assert before.endswith(b'\n')
addition=b'rosen.uni.partialrender.enabled=0\n'
after=before+addition
assert after[:-len(addition)]==before
entries[key]=(mode,after)
provenance=dict(parameter='rosen.uni.partialrender.enabled',value='0',
 source='original public parameter reader, DISABLED enum',
 archive_member=key,before_sha256=hashlib.sha256(before).hexdigest(),
 after_sha256=hashlib.sha256(after).hexdigest(),
 only_appended_line=True,original_images_modified=False,
 original_service_binaries_modified=False,original_security_checks_modified=False,
 runtime_parameter_read_verified=False,actual_desktop_verified=False)
(local/'partial-render-provenance.json').open('x').write(json.dumps(provenance,indent=2))
(local/'hw_defaults.para').open('xb').write(after)
'''
assert payload.count('def member(name,mode,data,ino):') == 1
payload = payload.replace('def member(name,mode,data,ino):', extra + '\ndef member(name,mode,data,ino):', 1)
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
