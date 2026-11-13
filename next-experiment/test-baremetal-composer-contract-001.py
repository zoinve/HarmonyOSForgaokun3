"""CPU-only characterization of actual reference composer admission and FD ownership.

Extract only these methods; no display initialization, DRM calls or GPU simulation.
"""
from pathlib import Path
import hashlib
import subprocess

reference=Path('C:/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/graphics')
raw=(reference/'composer.cpp').read_bytes()
text=raw.decode().replace('\r\n','\n')
constants=next(line for line in text.splitlines() if line.startswith('constexpr int OK ='))
assert constants=='constexpr int OK = 0, FAIL = -1, PARAM = -3, UNSUPPORTED = -5;'
def section(start,end):
    assert text.count(start)==1 and text.count(end)==1
    return text[text.index(start):text.index(end)]

source=r'''
#include <cassert>
#include <cerrno>
#include <cstdint>
#include <fcntl.h>
#include <mutex>
#include <poll.h>
#include <unistd.h>
#include <sys/eventfd.h>
#include <thread>
#include <chrono>
 #include "display_type.h"
'''+r'''
struct Rect { int32_t x,y,w,h; };
struct { std::mutex mutex; int client_fd=-1; BufferHandle client={}; Rect crop={}; } state;
'''+constants+r'''
#define API extern "C" int
'''+section('int wait_fence(int fence)','bool valid(const BufferHandle &buffer)')+section('bool valid(const BufferHandle &buffer)','int copy_client(Scanout &output)')+section('API SetDisplayClientBuffer(', 'API SetDisplayClientCrop(')+section('API ClearDisplayClientBuffer(', 'API Commit(')+r'''
int main() {
    int original=open("/dev/zero",O_RDONLY|O_CLOEXEC); assert(original>=0);
    BufferHandle buffer={};buffer.fd=original;buffer.width=13;buffer.height=7;
    buffer.stride=256;buffer.size=1792;buffer.format=PIXEL_FMT_RGBA_8888;
    assert(valid(buffer));
    auto bad=buffer;bad.stride=51;assert(!valid(bad));
    bad=buffer;bad.size=1791;assert(!valid(bad));
    bad=buffer;bad.usage=HBM_USE_PROTECTED;assert(!valid(bad));
    bad=buffer;bad.width=16385;assert(!valid(bad));
    bad=buffer;bad.format=-1;assert(!valid(bad));
    assert(SetDisplayClientBuffer(1,&buffer,-1)==PARAM && state.client_fd==-1);
    assert(SetDisplayClientBuffer(0,nullptr,-1)==PARAM && state.client_fd==-1);
    assert(SetDisplayClientBuffer(0,&buffer,-1)==OK);
    int held=state.client_fd;assert(held!=original);
    assert(fcntl(held,F_GETFD)&FD_CLOEXEC);
    close(original);unsigned char value=255;assert(read(held,&value,1)==1 && value==0);
    int next=open("/dev/null",O_RDONLY|O_CLOEXEC);assert(next>=0);buffer.fd=next;
    assert(SetDisplayClientBuffer(0,&buffer,1000000)==FAIL && state.client_fd==held);
    assert(fcntl(held,F_GETFD)>=0);
    int event=eventfd(0,EFD_CLOEXEC);assert(event>=0);
    std::thread signal([event] { std::this_thread::sleep_for(std::chrono::milliseconds(40));
        uint64_t one=1;assert(write(event,&one,sizeof(one))==sizeof(one)); });
    assert(SetDisplayClientBuffer(0,&buffer,event)==OK);signal.join();
    assert(fcntl(event,F_GETFD)>=0); // Caller still owns its fence descriptor.
    assert(fcntl(held,F_GETFD)==-1 && errno==EBADF);
    int replacement=state.client_fd;assert(replacement!=next);
    close(next);assert(read(replacement,&value,1)==0);
    assert(ClearDisplayClientBuffer(1)==PARAM && state.client_fd==replacement);
    assert(ClearDisplayClientBuffer(0)==OK && state.client_fd==-1);
    assert(fcntl(replacement,F_GETFD)==-1 && errno==EBADF);
    assert(ClearDisplayClientBuffer(0)==OK);close(event);
    return 0;
}
'''
headers={name:(reference/'include'/name).read_text() for name in ['buffer_handle.h','display_type.h']}
payload='source='+repr(source)+'\nheaders='+repr(headers)+'\n'+r'''
from pathlib import Path
import subprocess,tempfile
with tempfile.TemporaryDirectory(prefix='composer-contract001-') as directory:
    p=Path(directory);(p/'test.cpp').write_text(source)
    for name,text in headers.items():(p/name).write_text(text)
    subprocess.run(['c++','-std=c++17','-Wall','-Wextra','-Werror','-Wno-misleading-indentation','-pthread',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
    subprocess.run([str(p/'test')],check=True,timeout=10)
print('PASS: actual reference methods reject bad metadata, duplicate/replace/clear FDs, wait for poll readiness; CPU_ONLY no GPU/KMS/real sync_file')
'''
if __name__=='__main__':
    result=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=45)
    assert (reference/'composer.cpp').read_bytes()==raw
    print('reference_composer_sha256='+hashlib.sha256(raw).hexdigest())
    raise SystemExit(result.returncode)
