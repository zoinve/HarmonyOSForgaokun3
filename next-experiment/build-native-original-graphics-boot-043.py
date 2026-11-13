"""Fresh native callback-observation candidate; build only, no deployment or boot."""
from pathlib import Path
import runpy
import subprocess
import hashlib

base = Path(__file__).resolve().parent
project = base.parent
parent = runpy.run_path(str(base / 'build-native-original-graphics-boot-041.py'))
inner = parent['inner']
outer = parent['outer'].replace('native-interactive-041-%s', 'native-interactive-043-%s').replace('NATIVE_UNATTENDED041', 'NATIVE_UNATTENDED043')
frozen = project / 'reports/native-original-graphics-boot-041'
assert (frozen / 'bootstrap.c').read_bytes() == inner.encode()
assert (frozen / 'init.c').read_bytes() == parent['outer'].encode()
payload = parent['payload']
assert payload.count('outer=' + repr(parent['outer'])) == 1
payload = payload.replace('outer=' + repr(parent['outer']), 'outer=' + repr(outer), 1)
payload = payload.replace('native-original-graphics-boot-041', 'native-original-graphics-boot-043')
payload = payload.replace("root/'native-render-041'", "root/'native-presentation-043'")
payload = payload.replace("local/'render-041.json'", "local/'presentation-043.json'")
old = """for n,h in render_result['sha256'].items():assert sha(render_work/n)==h,n
assert render_result['sha256']['libcursor_drawing_adapter.z.so']==cursor_result['sha256']['libcursor_drawing_adapter.z.so']"""
assert payload.count(old) == 1
payload = payload.replace(old, """for n,row in render_result['files'].items():assert sha(render_work/n)==row['sha256'],n
old_render_work=root/'native-render-041'
old_render=json.loads((old_render_work/'result.json').read_text())
for n,h in old_render['sha256'].items():assert sha(old_render_work/n)==h,n
assert old_render['sha256']['libcursor_drawing_adapter.z.so']==cursor_result['sha256']['libcursor_drawing_adapter.z.so']
assert sha(render_work/'result.json')=='42e3b335598148c0482ca821a26215cdd7dd35a3ae1e806bb2112a4a0c521d65'""")
prefix = '''from pathlib import Path
import hashlib,json
original_work=Path('/home/zoinve/harmony-virgl-883/native-original-graphics-boot-041')
original_result=json.loads((original_work/'result.json').read_text())
original_guards={}
for row in original_result['artifacts']:
 p=original_work/row['name']
 with p.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
 assert p.stat().st_size==row['bytes'] and h==row['sha256'],str(p)
 original_guards[str(p)]=h
'''
payload = prefix + payload
payload += r'''

# A streaming, independent complete-archive comparison avoids multi-GiB decompression in memory.
import runpy,io
reader=runpy.run_path(str(project/'next-experiment/native-presentation-archive-043.py'))
scan_cpio=reader['scan_cpio']
vdi='native-target/graphics-provider/libdisplay_composer_vdi_impl.z.so'
scratch_name='native-target/scratch-data.ext4'
keep={'init',vdi}
def index(path, selected):
 with gzip.open(path,'rb') as stream:return scan_cpio(stream, selected)
old_index,_=index(original_work/'initrd.img',set())
new_index,new_small=index(work/'initrd.img',keep)
assert old_index.keys()==new_index.keys(), 'unexpected candidate file set'
changed=[]
for name in old_index:
 assert old_index[name]['metadata']==new_index[name]['metadata'], ('metadata drift',name)
 if old_index[name]['sha256']!=new_index[name]['sha256']:changed.append(name)
assert set(changed)=={'init',vdi,scratch_name}, changed
base_work=root/'native-original-graphics-boot-032'
base_manifest=json.loads((base_work/'result.json').read_text())
base_row=next(row for row in base_manifest['artifacts'] if row['name']=='initrd.img')
assert sha(base_work/'initrd.img')==base_row['sha256']
base_index,_=index(base_work/'initrd.img',set())
assert base_index.keys()==new_index.keys(), 'unexpected base032 file set'
for name in base_index:
 assert base_index[name]['metadata']==new_index[name]['metadata'], ('base metadata drift',name)
 if name not in keep|{scratch_name}:
  assert base_index[name]['sha256']==new_index[name]['sha256'], ('base payload drift',name)
# The last archive overrides only init and the real callback-instrumented VDI.
overlay_raw=b''.join(reader['emit_member'](name,new_index[name],new_small[name]) for name in ['init',vdi])+reader['trailer']()
overlay=work/'return-overlay.img'
with overlay.open('xb') as f:f.write(gzip.compress(overlay_raw,compresslevel=9,mtime=0))
overlay_index,_=scan_cpio(io.BytesIO(overlay_raw),keep)
assert set(overlay_index)==keep
for name in keep:assert overlay_index[name]==new_index[name]
for p,h in original_guards.items():assert sha(Path(p))==h,p
audit=dict(changed_vs041=changed,only_overlay_members=sorted(keep),
 scratch_reused_from_base032=True,base032_scratch=base_index[scratch_name],
 fresh_full_candidate_scratch=new_index[scratch_name],baseline041_files=len(old_index),
 preserved_vs041=len(old_index)-len(changed),streaming_archive_audit=True,
 base032_initrd_sha256=base_row['sha256'],full_candidate_initrd_sha256=sha(work/'initrd.img'),
 overlay=dict(path=str(overlay),bytes=overlay.stat().st_size,sha256=sha(overlay)),
 original_service_credentials_unmodified=True,original_images_readonly=True,
 automatic_input_injection=False,native_boot_attempted=False,installed=False,runtime_verified=False,
 desktop_fps_verified=False,submission_ids_are_visual_content_ids=False)
for dest in (work,local):
 with (dest/'presentation-overlay-audit.json').open('x') as f:json.dump(audit,f,indent=2)
print(json.dumps(audit,indent=2))
'''
compile(payload, 'native-presentation-candidate-043', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=900).returncode)
