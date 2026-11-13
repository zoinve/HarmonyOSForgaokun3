"""Execute reply admission: reject a real remote error once, retry absent/dead managers."""
from pathlib import Path
import subprocess

header=Path(__file__).with_name('baremetal-samgr-reply-action-044.h')
assert header.exists(), 'missing terminal-reply admission'
source=header.read_text()+r'''
#include <assert.h>
int main(void) {
    assert(samgr_reply_action_044(0, 0, -1) == 0);
    assert(samgr_reply_action_044(1, 0, -2) == 0);
    assert(samgr_reply_action_044(1, 1, 0) == 1);
    assert(samgr_reply_action_044(1, 1, 1) == -1);
    assert(samgr_reply_action_044(1, 1, -13) == -1);
    assert(samgr_reply_action_044(0, 1, 0) == 0);
    return 0;
}
'''
payload='source='+repr(source)+'\n'+r'''
from pathlib import Path
import subprocess,tempfile
with tempfile.TemporaryDirectory(prefix='samgr-reply044-') as directory:
    p=Path(directory);(p/'test.c').write_text(source)
    subprocess.run(['cc','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True)
    subprocess.run([str(p/'test')],check=True)
print('PASS: absent/dead manager retries, actual success admitted, remote rejection terminal')
'''
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=40)
    raise SystemExit(r.returncode)
