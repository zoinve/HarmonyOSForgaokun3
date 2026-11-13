"""Run native C policy checks; these do not claim GPU execution."""
from pathlib import Path
import subprocess

base = Path(__file__).resolve().parent
include = '/mnt/' + base.drive[0].lower() + base.as_posix()[2:]
source = r'''
#include <assert.h>
#include "baremetal-freedreno-policy-001.h"
int main(void) {
    assert(freedreno_renderer_ok("FD690"));
    assert(!freedreno_renderer_ok(NULL));
    assert(!freedreno_renderer_ok("virgl (FD690)"));
    assert(!freedreno_renderer_ok("llvmpipe (LLVM 19.1.7, 128 bits)"));
    assert(!freedreno_renderer_ok("softpipe"));
    assert(!freedreno_renderer_ok("FD660"));
    unsigned char center[] = {255,0,0,255}, corner[] = {0,0,255,255};
    assert(freedreno_pixels_ok(center,corner));
    center[0]=0; assert(!freedreno_pixels_ok(center,corner));
    center[0]=255; corner[2]=0; assert(!freedreno_pixels_ok(center,corner));
    corner[2]=255; center[3]=0; assert(!freedreno_pixels_ok(center,corner));
    center[3]=255; corner[1]=255; assert(!freedreno_pixels_ok(center,corner));
    return 0;
}
'''
payload = 'include=' + repr(include) + '\nsource=' + repr(source) + '\n' + r'''
import subprocess,tempfile
from pathlib import Path
with tempfile.TemporaryDirectory(prefix='freedreno-policy-test-',dir='/home/zoinve/harmony-virgl-883') as d:
    p=Path(d)/'test'
    subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-I'+include,'-x','c','-','-o',str(p)],input=source,text=True,check=True)
    subprocess.run([str(p)],check=True)
print('PASS: native C target-renderer admission and triangle pixel rejection checks')
'''
if __name__ == '__main__':
    subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,check=True,timeout=30)
