"""The WSI must upload typed VirGL buffers, preserving existing GL-state logic."""
from pathlib import Path
import runpy, subprocess
base = Path(__file__).resolve().parent
source = subprocess.check_output(['wsl','-d','Debian','--','cat','/home/zoinve/harmony-virgl-883/copy-error-911/bridge.cpp'], text=True)
transform = runpy.run_path(str(base/'gpu-gbm-copy.py'))['gbm_copy']
result = transform(source)
start = result.index('bool copy_frame')
part = result[start:result.index('\n}', start)]
assert 'gbm_bo_import' in part and 'GBM_BO_TRANSFER_WRITE' in part
assert 'gbm_bo_unmap' in part and 'gbm_bo_destroy' in part
assert 'mmap(nullptr, buffer.size' not in part
assert 'DMA_BUF_IOCTL_SYNC' not in part
assert 'size_t(y) * mapped_stride' in part
assert 'glReadPixels(0, 0, window.width, window.height' in part
assert 'buffer->usage & HBM_USE_PROTECTED' in result
print('PASS: typed GBM upload and mapping cleanup, real readback/validation retained')
