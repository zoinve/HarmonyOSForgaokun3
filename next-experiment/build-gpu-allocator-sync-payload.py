"""Fresh 906: verify flush while mapped and GPU-to-CPU invalidation, own buffers only."""
from pathlib import Path
base = Path(__file__).resolve().parent
# Expand the already verified builder transformation without editing old payloads.
builder = (base/'build-gpu-allocator-probe-payload.py').read_text()
builder = builder.replace('payload-903', 'payload-906').replace('command-probe-903', 'command-probe-906')
builder = builder.replace("work=root/'allocator-probe-903'", "work=root/'allocator-sync-906'")
builder = builder.replace('gpu903-buffer-vdi.so', 'gpu905-buffer-vdi.so')
anchor = "shutil.copy2(reference/'graphics/buffer_vdi.cpp',work/'buffer_vdi.cpp')"
extra = r'''
glClearColor(0.75f, 0.25f, 0.5f, 1.0f); glClear(GL_COLOR_BUFFER_BIT); glFinish();
require(glGetError() == GL_NO_ERROR, "GPU clear for invalidation");
require(!allocator->InvalidateCache(*handle), "invalidate while mapped");
printf("GPU906_INVALIDATE sample=%d rgba=%u,%u,%u,%u\n", sample, pixels[0], pixels[1], pixels[2], pixels[3]);
require(pixels[0]==191 && pixels[1]==64 && pixels[2]==128 && pixels[3]==255, "GPU-to-CPU content");
require(!allocator->Unmap(*handle), "unmap");
'''
setup = '''
import runpy
transform=runpy.run_path(str(local/'gpu-gbm-vdi.py'))['gbm_vdi']
(work/'buffer_vdi.cpp').write_text(transform((reference/'graphics/buffer_vdi.cpp').read_text()))
probe=(local/'gpu-allocator-probe.cpp').read_text()
assert probe.count('require(!allocator->Unmap(*handle), "unmap");') == 1
probe=probe.replace('require(!allocator->Unmap(*handle), "unmap");', '// Keep the CPU mapping live to validate FlushCache independently.')
anchor='glBindFramebuffer(GL_FRAMEBUFFER, 0); glDeleteFramebuffers(1, &fbo);'
assert probe.count(anchor)==1
probe=probe.replace(anchor, EXTRA_CODE + anchor)
(work/'probe.cpp').write_text(probe)
'''
builder = builder.replace(anchor, setup.replace('EXTRA_CODE', repr(extra)))
builder = builder.replace("'-L'+str(libs),'-ldrm',str(work/'libbuffer_handle.z.so')", "'-L'+str(libs),'-lgbm','-ldrm',str(work/'libbuffer_handle.z.so')")
builder = builder.replace("str(local/'gpu-allocator-probe.cpp')", "str(work/'probe.cpp')")
exec(compile(builder, str(base/'build-gpu-allocator-probe-payload.py'), 'exec'), {'__file__': str(base/'build-gpu-allocator-probe-payload.py')})
