"""Fresh 895: inspect the failed GBM backend load; preserve EGL return values."""
from pathlib import Path

base = Path(__file__).resolve().parent
source = (base / 'build-gpu-display-trace-payload.py').read_text()
anchor = "(work/'bridge.cpp').write_text(bridge)"
assert source.count(anchor) == 1
addition = r'''
old=' gpu892_trace("GPU894_GBM device=%p errno=%d\\n",display.device,errno);'
assert bridge.count(old)==1
bridge=bridge.replace(old,old+r"""
    if (!display.device) {
        int saved_errno=errno;
        gpu892_trace("GPU895_ID uid=%u euid=%u gid=%u egid=%u backend_env=%s\n",
            (unsigned)getuid(),(unsigned)geteuid(),(unsigned)getgid(),(unsigned)getegid(),
            getenv("GBM_BACKENDS_PATH")?getenv("GBM_BACKENDS_PATH"):"NULL");
        void *backend=dlopen("/system/lib64/lab-softpipe-167/gbm/dri_gbm.so",RTLD_NOW|RTLD_LOCAL);
        const char *load_error=dlerror();
        gpu892_trace("GPU895_BACKEND handle=%p error=%s\n",backend,load_error?load_error:"none");
        if(backend) {
            void *entry=dlsym(backend,"gbmint_get_backend");
            const char *symbol_error=dlerror();
            gpu892_trace("GPU895_BACKEND_ENTRY address=%p error=%s\n",entry,symbol_error?symbol_error:"none");
            dlclose(backend);
        }
        errno=saved_errno;
    }
""")
'''
source = source.replace(anchor, addition + '\n' + anchor)
source = source.replace('payload-894', 'payload-895').replace('command-probe-894', 'command-probe-895').replace('display-trace-894', 'backend-trace-895')
exec(compile(source, str(base / 'build-gpu-display-trace-payload.py'), 'exec'), {'__file__': __file__})
