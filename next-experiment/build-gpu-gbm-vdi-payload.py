"""Fresh 905: independent GBM-backed VDI test; system allocator unchanged."""
from pathlib import Path
base = Path(__file__).resolve().parent
text = (base/'build-gpu-allocator-probe-payload.py').read_text()
text = text.replace('payload-903', 'payload-905').replace('command-probe-903', 'command-probe-905')
text = text.replace("work=root/'allocator-probe-903'", "work=root/'gbm-vdi-905'")
text = text.replace('gpu903-buffer-vdi.so', 'gpu905-buffer-vdi.so')
anchor = "shutil.copy2(reference/'graphics/buffer_vdi.cpp',work/'buffer_vdi.cpp')"
assert text.count(anchor) == 1
text = text.replace(anchor, '''
import runpy
transform=runpy.run_path(str(local/'gpu-gbm-vdi.py'))['gbm_vdi']
(work/'buffer_vdi.cpp').write_text(transform((reference/'graphics/buffer_vdi.cpp').read_text()))
''')
text = text.replace("'-L'+str(libs),'-ldrm',str(work/'libbuffer_handle.z.so')", "'-L'+str(libs),'-lgbm','-ldrm',str(work/'libbuffer_handle.z.so')")
exec(compile(text, str(base/'build-gpu-allocator-probe-payload.py'), 'exec'), {'__file__': str(base/'build-gpu-allocator-probe-payload.py')})
