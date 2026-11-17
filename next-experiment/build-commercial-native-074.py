"""Native integration of real linear YUV/BLOB and two-plane EGL import."""
from pathlib import Path
import runpy

b = Path(__file__).resolve().parent
p = runpy.run_path(str(b / 'build-commercial-native-073.py'))
module = runpy.run_path(str(b / 'commercial-yuv-074.py'))
inner = module['replace_once'](p['inner'], '"/allocator073/libdisplay_buffer_vdi_impl.z.so"',
                             '"/allocator074/libdisplay_buffer_vdi_impl.z.so"')
egl_anchor = 'commercial_copy005("/graphics016/system/lib64/libEGL_impl.so",'
assert inner.count(egl_anchor) == 2
inner = inner.replace(egl_anchor, 'commercial_copy005("/egl074/libEGL_impl.so",')
outer = p['outer'].replace('commercial61-native-073', 'commercial61-native-074').replace('COMMERCIAL073', 'COMMERCIAL074')
payload = p['payload'].replace('inner=' + repr(p['inner']), 'inner=' + repr(inner), 1).replace(
    'outer=' + repr(p['outer']), 'outer=' + repr(outer), 1)
payload = payload.replace('commercial61-native-073', 'commercial61-native-074')
anchor = 'def member(name,mode,data,ino):'
assert payload.count(anchor) == 1
addition = """
yuv074=root/'commercial-yuv-074-r3'
provenance074=json.loads((yuv074/'result.json').read_text())
for role074,folder074,name074 in [('allocator','allocator074','libdisplay_buffer_vdi_impl.z.so'),
                                ('egl','egl074','libEGL_impl.so')]:
 body074=(yuv074/name074).read_bytes()
 assert hashlib.sha256(body074).hexdigest()==provenance074['artifacts'][role074]['binary_sha256']
 assert 'native-target/'+folder074 not in entries
 entries['native-target/'+folder074]=(stat.S_IFDIR|0o755,b'')
 entries['native-target/'+folder074+'/'+name074]=(stat.S_IFREG|0o755,body074)
(local/'yuv-provenance.json').open('x').write(json.dumps(provenance074,indent=2))
"""
payload = payload.replace(anchor, addition + '\n' + anchor, 1)
if __name__ == '__main__':
    exec(compile(payload, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
