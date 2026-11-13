"""Place console on RAM tmpfs, matching original policy's authorized relabel source."""
from pathlib import Path
import runpy
import subprocess

parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-selinux-load-017.py')))
source=parent['source'].replace('#include <sys/xattr.h>','#include <sys/xattr.h>\n#include <sys/sysmacros.h>')
anchor='    const char console_context[] = "u:object_r:dev_console_file:s0";'
assert source.count(anchor)==1
source=source.replace(anchor,'''    require(!mount("tmpfs", "/dev", "tmpfs", MS_NOSUID, "mode=0755"), "RAM-only device filesystem");
    require(!mknod("/dev/console", S_IFCHR | 0600, makedev(5, 1)), "RAM console node");
    int console_fd = open("/dev/console", O_RDWR | O_CLOEXEC);
    require(console_fd >= 0 && dup2(console_fd, 0) == 0 && dup2(console_fd, 1) == 1 &&
            dup2(console_fd, 2) == 2, "console on RAM device filesystem");
    close(console_fd);
'''+anchor)
anchor='    char actual_context[128] = {0};'
assert source.count(anchor)==1
source=source.replace(anchor,'''    console_fd = open("/dev/console", O_RDWR | O_CLOEXEC);
    require(console_fd >= 0 && dup2(console_fd, 0) == 0 && dup2(console_fd, 1) == 1 &&
            dup2(console_fd, 2) == 2, "reopen console in authorized init domain");
    close(console_fd);
'''+anchor).replace('SELINUX017_','SELINUX018_')
payload='source='+repr(source)+'\n'+parent['payload'][parent['payload'].index('\nfrom pathlib import Path')+1:]
payload=payload.replace('baremetal-selinux-load-017','baremetal-selinux-load-018')
compile(payload,'selinux-018-preparation','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)
