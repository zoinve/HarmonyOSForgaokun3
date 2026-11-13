"""Fresh 909: observe allocator backend environment and loader failures only."""
from pathlib import Path

base = Path(__file__).resolve().parent
source = (base/'build-gpu-allocator-trace-payload.py').read_text()
source = source.replace('908', '909').replace('allocator-trace-909', 'allocator-backend-909')
anchor = "(work/'buffer_vdi.cpp').write_text(source)"
extra = r'''
source=source.replace('#include <cstdlib>', '#include <cstdlib>\n#include <dlfcn.h>')
source=source.replace('AURORA_VDI_LOG("FACTORY uid=%d gid=%d",getuid(),getgid());',
    'AURORA_VDI_LOG("FACTORY uid=%d euid=%d gid=%d egid=%d GBM=%s GALLIUM=%s SOFTWARE=%s OVERRIDE=%s LD=%s",getuid(),geteuid(),getgid(),getegid(),getenv("GBM_BACKENDS_PATH"),getenv("GALLIUM_DRIVER"),getenv("LIBGL_ALWAYS_SOFTWARE"),getenv("MESA_LOADER_DRIVER_OVERRIDE"),getenv("LD_LIBRARY_PATH"));')
needle='return gbm_ != nullptr;'
assert source.count(needle)==1
source=source.replace(needle, 'if (!gbm_) { int saved=errno; void *backend=dlopen("/system/lib64/lab-softpipe-167/gbm/dri_gbm.so",RTLD_NOW|RTLD_LOCAL); const char *error=dlerror(); AURORA_VDI_LOG("BACKEND handle=%p error=%s",backend,error?error:"none"); if(backend)dlclose(backend); errno=saved; } '+needle)
'''
assert source.count(anchor) == 1
source = source.replace(anchor, extra+'\n'+anchor)
source = source.replace("'-lgbm','-ldrm'", "'-lgbm','-ldrm','-ldl'")
exec(compile(source, str(base/'build-gpu-allocator-trace-payload.py'), 'exec'), {'__file__': str(base/'build-gpu-allocator-trace-payload.py')})
