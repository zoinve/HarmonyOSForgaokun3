"""Own EGL/HDI hardware bridges rebuilt for the commercial runtime; offline only."""
from pathlib import Path
import runpy,subprocess,sys
p=runpy.run_path(str(Path(__file__).with_name('build-commercial-graphics-link-009.py')))
payload=p['payload'].replace("work=r/'commercial-graphics-link-009';local=base.parent/'reports/commercial-graphics-link-009'", "work=r/'commercial-graphics-014';local=base.parent/'reports/commercial-graphics-014'")
anchor="shutil.copyfile(old/'native-cursor-composer-041.h',work/'native-cursor-composer-041.h')"
extra=r'''
source=work/'composer-trace.cpp';text=source.read_text()
assert text.count('/system/lib64/lab-freedreno003/')==1
source.write_text(text.replace('/system/lib64/lab-freedreno003/','/system/lib64/lab-commercial013/'))
'''
assert payload.count(anchor)==1
payload=payload.replace(anchor,anchor+'\n'+extra)
anchor='data=dict(sha256='
extra=r'''
mesa=r/'commercial-mesa-013/stage/system/lib64/lab-commercial013'
mesa_result=json.loads((r/'commercial-mesa-013/result.json').read_text())
assert mesa_result['build_success'] and not mesa_result['sdk_runtime_libraries_used']
egl_source=r/'native-original-graphics-boot-032/egl-perf-023.cpp'
egl_text=egl_source.read_text();egl_original_sha=sha(egl_source)
assert egl_text.count('/system/lib64/lab-freedreno003/')==1
egl_text=egl_text.replace('/system/lib64/lab-freedreno003/','/system/lib64/lab-commercial013/')
(work/'egl-commercial-014.cpp').write_text(egl_text)
egl_cmd=[x.replace(str(work/'composer-trace.cpp'),str(work/'egl-commercial-014.cpp'))
 .replace(str(work/'libdisplay_composer_vdi_impl.z.so'),str(work/'libEGL_impl.so'))
 .replace('-soname,libdisplay_composer_vdi_impl.z.so','-soname,libEGL_impl.so')
 .replace('-rpath,/vendor/lib64/harmony-graphics','-rpath,/system/lib64/lab-commercial013')
 for x in cmd]
egl_cmd+=['-DEGL_EGLEXT_PROTOTYPES',str(mesa/'libGLESv2.so.2'),str(mesa/'libgbm.so.1')]
with (work/'egl-link.stdout').open('xb') as out,(work/'egl-link.stderr').open('xb') as err:
 egl_status=subprocess.run(egl_cmd,stdout=out,stderr=err,timeout=120)
for n in ['egl-link.stdout','egl-link.stderr']:shutil.copyfile(work/n,local/n)
assert egl_status.returncode==0,(work/'egl-link.stderr').read_text()
assert sha(egl_source)==egl_original_sha
graphics_sha256={n:sha(work/n) for n in ['libdisplay_composer_vdi_impl.z.so','libEGL_impl.so']}
graphics_link_traces={'libdisplay_composer_vdi_impl.z.so':'link.stdout'+suffix,'libEGL_impl.so':'egl-link.stdout'}
for n in graphics_link_traces.values():
 t=(work/n).read_text();assert '/platform-root/' not in t
 assert not any('/sdk/' in l and l.strip().endswith('.so') for l in t.splitlines())
'''
assert payload.count(anchor)==1
payload=payload.replace(anchor,extra+'\n'+anchor,1)
payload=payload.replace('commands=[cmd],link_trace_file=', 'graphics_sha256=graphics_sha256,graphics_link_traces=graphics_link_traces,commands=[cmd,egl_cmd],link_trace_file=',1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-']+sys.argv[1:],input=payload,text=True,timeout=360).returncode)
