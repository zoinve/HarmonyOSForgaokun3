"""Fresh 896: compare an independently opened render node; do not change EGL results."""
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
        int render_fd=open("/dev/dri/renderD128",O_RDWR|O_CLOEXEC);
        int open_errno=errno;
        gbm_device *render_device=render_fd>=0?gbm_create_device(render_fd):nullptr;
        int create_errno=errno;
        gpu892_trace("GPU896_RENDER_NODE fd=%d open_errno=%d device=%p create_errno=%d uid=%u euid=%u gid=%u egid=%u\n",
            render_fd,render_fd<0?open_errno:0,render_device,render_device?0:create_errno,
            (unsigned)getuid(),(unsigned)geteuid(),(unsigned)getgid(),(unsigned)getegid());
        if(render_device)gbm_device_destroy(render_device);
        if(render_fd>=0)close(render_fd);
        errno=saved_errno;
    }
""")
'''
source = source.replace(anchor, addition + '\n' + anchor)
source = source.replace('payload-894', 'payload-896').replace('command-probe-894', 'command-probe-896').replace('display-trace-894', 'rendernode-trace-896')
exec(compile(source, str(base / 'build-gpu-display-trace-payload.py'), 'exec'), {'__file__': __file__})
