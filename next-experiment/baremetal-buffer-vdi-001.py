"""Generate a private render-only reference adaptation; never edit the reference."""
from pathlib import Path
import hashlib
import runpy


def build_source(reference):
    assert isinstance(reference, bytes)
    assert hashlib.sha256(reference).hexdigest()=='16780fc008e1c1c5131afb0b4e358a7bac9e8ea3ac89df4c2a7e5d6b789b4a0f'
    reference=reference.decode().replace('\r\n','\n')
    base=Path(__file__).resolve().parent
    source=runpy.run_path(str(base/'gpu-gbm-vdi.py'))['gbm_vdi'](reference)
    anchor='if (display_.fd < 0 && AuroraOpenDisplayDrm(&display_, 0)) return false;'
    assert source.count(anchor)==1
    source=source.replace(anchor,'''if (display_.fd < 0) {
            int fd=open("/dev/dri/renderD128", O_RDWR | O_CLOEXEC);
            if (fd < 0) return false;
            struct stat state;
            if (fstat(fd, &state) || !native_render_identity001(&state)) {
                close(fd); return false;
            }
            drmVersion *version=drmGetVersion(fd);
            bool msm=version && version->name && !strcmp(version->name,"msm");
            if (version) drmFreeVersion(version);
            if (!msm) { close(fd); return false; }
            display_.fd=fd;
        }''')
    source=source.replace('#include <gbm.h>','#include <gbm.h>\n'+(base/'baremetal-render-node-policy-001.h').read_text())
    assert 'AuroraOpenDisplayDrm(' not in source
    assert 'DRM_IOCTL_MODE_CREATE_DUMB' not in source
    assert 'drmSetMaster(' not in source
    return source
