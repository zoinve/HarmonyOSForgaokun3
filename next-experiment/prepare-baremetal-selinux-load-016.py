"""Use original console label and policy-authorized init transition, without changing policy."""
from pathlib import Path
import runpy
import subprocess

source=Path(__file__).with_name('baremetal-selinux-load-013.c').read_text()
source=source.replace('#include <sys/stat.h>','#include <sys/stat.h>\n#include <sys/xattr.h>')
anchor='    fd = open("/sys/fs/selinux/load", O_WRONLY | O_CLOEXEC);'
assert source.count(anchor)==1
source=source.replace(anchor,'''    const char console_context[] = "u:object_r:dev_console_file:s0";
    require(!setxattr("/dev/console", "security.selinux", console_context,
                     sizeof(console_context), 0), "original console security label");
'''+anchor)
anchor='    dprintf(1, "SELINUX013_LOAD bytes=%zu result=%zd errno=%d\\n", size, written, load_errno);'
assert source.count(anchor)==1
source=source.replace(anchor,'''    require(written == (ssize_t)size, "original policy load result");
    errno = 0;
    const char forbidden[] = "UNEXPECTED_KERNEL_DOMAIN_CONSOLE_WRITE\\n";
    require(write(1, forbidden, sizeof(forbidden)-1) == -1 && errno == EACCES,
            "kernel domain must not write init console");
    int context_fd = open("/proc/self/attr/current", O_WRONLY | O_CLOEXEC);
    const char init_context[] = "u:r:init:s0";
    require(context_fd >= 0 && write(context_fd, init_context, sizeof(init_context)-1) == sizeof(init_context)-1,
            "original policy authorized kernel to init transition");
    close(context_fd);
'''+anchor)
source=source.replace('strstr(buffer, ":kernel:")','strstr(buffer, ":init:")').replace('policy-mapped initial kernel domain','policy-authorized init domain')
source=source.replace('services_not_tested=1 desktop_not_tested=1','kernel_console_denied=1 authorized_init_transition=1 services_not_tested=1 desktop_not_tested=1')
source=source.replace('SELINUX013_','SELINUX016_')
parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-selinux-load-013.py')))['payload']
payload='source='+repr(source)+'\n'+parent[parent.index('\nfrom pathlib import Path')+1:]
payload=payload.replace('baremetal-selinux-load-013','baremetal-selinux-load-016')
anchor="policy=dump('vendor.img'"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"""contexts=dump('system.img','/system/etc/selinux/targeted/contexts/file_contexts','original-file-contexts')
console_lines=[line for line in contexts.read_text().splitlines() if line.split() and line.split()[0]=='/dev/console']
assert console_lines and all(line.split()[-1]=='u:object_r:dev_console_file:s0' for line in console_lines),console_lines
"""+anchor)
compile(payload,'selinux-016-preparation','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)
