"""Run real launcher admission code; no GPU, mounts, or privilege changes in this test."""
from pathlib import Path
import subprocess

base=Path(__file__).resolve().parent
path=base/'baremetal-mesa-launcher-001.c'
assert path.exists(), 'missing native Mesa sandbox launcher'
source=path.read_text()
harness=r'''
#undef main
#include <assert.h>
int main(void) {
    const char *release="7.1.0-rc3-gaokun3-el2";
    assert(mesa_gate(0,release,"harmony.diag=1 enforcing=1")==0);
    assert(mesa_gate(0,release,"enforcing=1\nharmony.diag=1\t")==0);
    assert(mesa_gate(1001,release,"harmony.diag=1 enforcing=1")!=0);
    assert(mesa_gate(0,"7.1.0-rc3-gaokun3+","harmony.diag=1 enforcing=1")!=0);
    assert(mesa_gate(0,release,"harmony.diag=1")!=0);
    assert(mesa_gate(0,release,"harmony.diag=1 enforcing=0")!=0);
    assert(mesa_gate(0,release,"harmony.diag=1 enforcing=1 enforcing=0")!=0);
    assert(mesa_gate(0,release,"harmony.diag=1 harmony.diag=1 enforcing=1")!=0);
    assert(mesa_gate(0,release,"xharmony.diag=1 enforcing=1")!=0);
    return 0;
}
'''
payload='source='+repr('#define main launcher_main\n'+source+harness)+'\n'+r'''
from pathlib import Path
import tempfile,subprocess
with tempfile.TemporaryDirectory(prefix='native-mesa-gate001-') as directory:
    p=Path(directory);(p/'test.c').write_text(source)
    subprocess.run(['cc','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True)
    subprocess.run([str(p/'test')],check=True)
print('PASS: real launcher admission rejects wrong kernel/UID/missing or duplicated boot opt-ins')
'''
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=40)
    raise SystemExit(r.returncode)
