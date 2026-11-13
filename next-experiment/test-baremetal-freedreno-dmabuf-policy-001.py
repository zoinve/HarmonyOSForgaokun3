"""Run real native C rejection checks before any DMA-BUF import is attempted."""
from pathlib import Path
import subprocess

header=Path(__file__).with_name('baremetal-freedreno-dmabuf-policy-001.h')
assert header.exists(), 'missing DMA-BUF metadata admission policy'
code=r'''
#include <assert.h>
#include <limits.h>
#include "baremetal-freedreno-dmabuf-policy-001.h"
int main(void) {
    assert(dmabuf_meta_ok(0,16,16,1,64,0,0));
    assert(dmabuf_meta_ok(9,16,16,1,128,0,0));
    assert(!dmabuf_meta_ok(-1,16,16,1,64,0,0));
    assert(!dmabuf_meta_ok(9,0,16,1,64,0,0));
    assert(!dmabuf_meta_ok(9,16,0,1,64,0,0));
    assert(!dmabuf_meta_ok(9,16,16,2,64,0,0));
    assert(!dmabuf_meta_ok(9,16,16,1,63,0,0));
    assert(!dmabuf_meta_ok(9,16,16,1,64,1,0));
    assert(!dmabuf_meta_ok(9,16,16,1,64,0,1));
    assert(!dmabuf_meta_ok(9,UINT_MAX,16,1,64,0,0));
    assert(!dmabuf_meta_ok(9,16,16,1,UINT_MAX,0,0));
    return 0;
}
'''
payload='code='+repr(code)+'\nheader='+repr(header.read_text())+'\n'+r'''
from pathlib import Path
import subprocess,tempfile
with tempfile.TemporaryDirectory(prefix='dmabuf-policy-',dir='/home/zoinve/harmony-virgl-883') as t:
 p=Path(t);(p/'test.c').write_text(code);(p/'baremetal-freedreno-dmabuf-policy-001.h').write_text(header)
 subprocess.run(['cc','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True)
 subprocess.run([str(p/'test')],check=True)
print('PASS: real C DMA-BUF FD, dimensions, plane count, stride, offset and modifier rejection checks')
'''
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,check=True,timeout=30)
