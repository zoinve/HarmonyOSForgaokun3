"""Fail before implementing the native GPU transfer candidate; no target execution."""
from pathlib import Path
import runpy, subprocess
base=Path(__file__).resolve().parent
header=base/'native-gpu-copy-025.h'
assert header.exists(),'missing DMA-BUF GPU transfer implementation'
s=header.read_text()
for required in ['EGL_LINUX_DMA_BUF_EXT','glBlitFramebuffer','GL_FRAMEBUFFER_COMPLETE',
                 'GL_READ_FRAMEBUFFER_BINDING','GL_DRAW_FRAMEBUFFER_BINDING',
                 'GL_RENDERBUFFER_BINDING','GL_SCISSOR_TEST','EGL_SYNC_NATIVE_FENCE_ANDROID']:
    assert required in s,required
for forbidden in ['glReadPixels(', 'mmap(', 'memcpy(', 'DMA_BUF_SYNC']:
    assert forbidden not in s,forbidden
b=runpy.run_path(str(base/'build-native-original-graphics-boot-025.py'))
assert b['inner']==b['p']['inner'],'do not change service identities, input or configuration'
assert 'copy_frame_gpu_025' in b['payload']
assert 'flush(window->native, buffer, release_fence_025' in b['payload']
q=runpy.run_path(str(base/'test-native-original-graphics-boot-001.py'))
payload=q['payload'].replace('native-original-graphics-boot-001','native-original-graphics-boot-025')
if __name__=='__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True).returncode)
