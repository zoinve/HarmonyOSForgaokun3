"""Observe exact Binder error and kernel state, without substituting a service or changing policy."""
from pathlib import Path
import runpy
import subprocess

parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-samgr-exec-031.py')))
source=parent['source']
anchor='    int fd = open("/sys/fs/selinux/load", O_WRONLY | O_CLOEXEC);'
# The inherited policy loader declares the load FD before the invalid-policy test.
assert source.count(anchor)==1
source=source.replace(anchor,'''    require(!mkdir("/debug",0755) && !mount("debugfs","/debug","debugfs",MS_NOSUID|MS_NODEV|MS_NOEXEC,NULL),
            "isolated kernel Binder diagnostic filesystem");
'''+anchor)
anchor='    char path[256], value[16384];'
assert source.count(anchor)==1
source=source.replace(anchor,anchor+'''
    const char *binder_files[] = {"state","stats","failed_transaction_log","transaction_log"};
    for (unsigned i=0; i<4; ++i) {
        snprintf(path,sizeof(path),"/debug/binder/%s",binder_files[i]);
        errno=0; int n=text(path,value,sizeof(value));
        dprintf(1,"SELINUX032_BINDER path=%s count=%d errno=%d\\n%s\\n",path,n,errno,n>0?value:"");
    }
''')
anchor='                received = 1; result = -2;'
assert source.count(anchor)==1
source=source.replace(anchor,'''                dprintf(1,"SELINUX032_BINDER_ERROR command=0x%x dead=%d failed=%d\\n",
                        op,op==BR_DEAD_REPLY,op==BR_FAILED_REPLY);
'''+anchor)
source=source.replace('SELINUX031_','SELINUX032_')
payload='source='+repr(source)+'\n'+parent['payload'][parent['payload'].index('\nfrom pathlib import Path')+1:]
payload=payload.replace('baremetal-sdk-samgr-exec-031','baremetal-sdk-samgr-exec-032')
compile(payload,'samgr-exec032-preparation','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)
