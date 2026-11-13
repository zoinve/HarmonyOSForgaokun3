"""Extract only actual client-buffer methods into a private bridge, never a full composer VDI."""
from pathlib import Path
import hashlib

def build_sources():
    root=Path('C:/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/graphics')
    raw=(root/'composer.cpp').read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='9d2536a61c40aef948f48c482a081cdc2794d832d0775cee6bd9de87bdfa1b5a'
    text=raw.decode().replace('\r\n','\n')
    def section(start,end):
        assert text.count(start)==1 and text.count(end)==1
        return text[text.index(start):text.index(end)]
    constants=next(l for l in text.splitlines() if l.startswith('constexpr int OK ='))
    assert constants=='constexpr int OK = 0, FAIL = -1, PARAM = -3, UNSUPPORTED = -5;'
    source=r'''
#include <cerrno>
#include <cstdint>
#include <climits>
#include <fcntl.h>
#include <mutex>
#include <poll.h>
#include <unistd.h>
#include "display_type.h"
struct Rect {int32_t x,y,w,h;};
struct {std::mutex mutex; int client_fd=-1; BufferHandle client={}; Rect crop={};} state;
'''+constants+'\nstatic_assert(UNSUPPORTED == -5, "reference error constant");\n#define API extern "C" int\n'
    for start,end in [('int wait_fence(int fence)','bool valid(const BufferHandle &buffer)'),
                      ('bool valid(const BufferHandle &buffer)','int copy_client(Scanout &output)'),
                      ('API SetDisplayClientBuffer(','API SetDisplayClientCrop('),
                      ('API ClearDisplayClientBuffer(','API Commit(')]:
        source+=section(start,end)
    source+=r'''
extern "C" int composer_accept001(int fd,int fence,uint32_t width,uint32_t height,uint32_t stride)
{
    if(width>INT_MAX || height>INT_MAX || stride>INT_MAX ||
       (uint64_t)stride*height>INT_MAX)return PARAM;
    BufferHandle handle={};handle.fd=fd;handle.width=(int32_t)width;
    handle.height=(int32_t)height;handle.stride=(int32_t)stride;
    handle.size=(int32_t)((uint64_t)stride*height);
    handle.format=PIXEL_FMT_BGRA_8888;
    return SetDisplayClientBuffer(0,&handle,fence);
}
/* Borrowed for this single-threaded diagnostic only; clear invalidates this FD. */
extern "C" int composer_borrow001(void) {return state.client_fd;}
extern "C" int composer_clear001(void) {return ClearDisplayClientBuffer(0);}
'''
    for forbidden in ['InitDisplay(', 'Commit(', 'drmMode', '/dev/dri/card', 'ioctl(']:
        assert forbidden not in source,forbidden
    return {'bridge.cpp':source,**{name:(root/'include'/name).read_text() for name in ['display_type.h','buffer_handle.h']}}
