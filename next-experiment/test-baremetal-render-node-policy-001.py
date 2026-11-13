"""Actual native C admission checks; fabricated stat records are not GPU evidence."""
from pathlib import Path
import subprocess

header=Path(__file__).with_name('baremetal-render-node-policy-001.h')
assert header.exists(), 'missing exact render-node admission'
source=header.read_text()+r'''
#include <assert.h>
int main(void) {
    struct stat s = {0};
    assert(!native_render_identity001(0));
    s.st_mode=S_IFREG|0600;s.st_rdev=makedev(226,128);
    assert(!native_render_identity001(&s));
    s.st_mode=S_IFCHR|0660;s.st_rdev=makedev(226,0);
    assert(!native_render_identity001(&s));
    s.st_rdev=makedev(1,128);assert(!native_render_identity001(&s));
    s.st_rdev=makedev(226,129);assert(!native_render_identity001(&s));
    s.st_rdev=makedev(226,128);assert(native_render_identity001(&s));
    return 0;
}
'''
payload='source='+repr(source)+'\n'+r'''
from pathlib import Path
import tempfile,subprocess
with tempfile.TemporaryDirectory(prefix='render-admission001-') as d:
    p=Path(d);(p/'test.c').write_text(source)
    subprocess.run(['cc','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True)
    subprocess.run([str(p/'test')],check=True)
print('PASS: only character node 226:128 admitted; GPU not tested')
'''
if __name__=='__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=40).returncode)
