"""Replace only EGL CPU readback with actual DMA-BUF GPU blits and real fences."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-native-original-graphics-boot-024.py'))
inner=p['inner'];outer=p['outer'].replace('native-original-024-%s','native-original-025-%s')
payload=p['payload'].replace('native-original-graphics-boot-024','native-original-graphics-boot-025')
assert 'outer='+repr(p['outer']) in payload
payload=payload.replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
adapt=r'''
gpu_header=project/'next-experiment/native-gpu-copy-025.h'
(work/gpu_header.name).write_bytes(gpu_header.read_bytes())
start=egl.index('// Preserve application pack state, including ES3 PBO/row offsets and read FBO.')
end=egl.index('\n}\n\nnamespace OHOS {',start)
# Leave the namespace closing brace and every original NativeWindow operation intact.
egl=egl[:start]+'#include "native-gpu-copy-025.h"\n'+egl[end:]
egl=egl.replace('    bool waited = wait_fence(fence);','    int release_fence_025=-1;\n    bool waited = wait_fence(fence);')
assert egl.count('!copy_frame(*window, *handle)')==1
egl=egl.replace('!copy_frame(*window, *handle)','!copy_frame_gpu_025(*window, *handle,release_fence_025)')
assert egl.count('flush(window->native, buffer, -1,')==1
egl=egl.replace('flush(window->native, buffer, -1,','flush(window->native, buffer, release_fence_025,')
with (local/'gpu-transfer-025.json').open('x') as f:
 json.dump(dict(source_sha256=sha(gpu_header),cpu_readback_removed=True,gpu_dma_buf_import=True,
  native_release_fence=True,composer_cpu_rotation_still_present=True,stable_120fps_verified=False),f,indent=2)
'''
anchor="egl_src=work/'egl-perf-023.cpp';egl_src.write_text(egl)"
assert payload.count(anchor)==1
payload=payload.replace(anchor,adapt+'\n'+anchor)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
