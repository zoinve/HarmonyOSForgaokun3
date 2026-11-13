"""Check denial on the deliberately wrong rootfs console, not the valid RAM console."""
from pathlib import Path
import runpy
import subprocess

parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-selinux-load-018.py')))
source=parent['source']
anchor='    require(!mount("tmpfs", "/dev", "tmpfs", MS_NOSUID, "mode=0755"), "RAM-only device filesystem");'
assert source.count(anchor)==1
source=source.replace(anchor,'''    int forbidden_fd = dup(1);
    require(forbidden_fd >= 0, "retain wrongly labelled rootfs console as negative fixture");
'''+anchor)
negative='''    errno = 0;
    const char forbidden[] = "UNEXPECTED_KERNEL_DOMAIN_CONSOLE_WRITE\\n";
    require(write(1, forbidden, sizeof(forbidden)-1) == -1 && errno == EACCES,
            "kernel domain must not write init console");
'''
assert source.count(negative)==1
source=source.replace(negative,'')
anchor='    dprintf(1, "SELINUX018_LOAD bytes=%zu result=%zd errno=%d\\n", size, written, load_errno);'
assert source.count(anchor)==1
source=source.replace(anchor,'''    errno = 0;
    const char forbidden[] = "UNEXPECTED_ROOTFS_CONSOLE_WRITE\\n";
    require(write(forbidden_fd, forbidden, sizeof(forbidden)-1) == -1 && errno == EACCES,
            "policy must deny wrongly labelled rootfs console");
    close(forbidden_fd);
'''+anchor).replace('kernel_console_denied=1','rootfs_console_denied=1').replace('SELINUX018_','SELINUX019_')
payload='source='+repr(source)+'\n'+parent['payload'][parent['payload'].index('\nfrom pathlib import Path')+1:]
payload=payload.replace('baremetal-selinux-load-018','baremetal-selinux-load-019')
compile(payload,'selinux-019-preparation','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)
