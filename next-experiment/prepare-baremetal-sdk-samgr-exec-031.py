"""Diagnose original samgr startup wait points; retain failed ping as a failure."""
from pathlib import Path
import runpy
import subprocess

parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-samgr-exec-030.py')))
source=parent['source']
anchor='static int samgr_ping_030(void)'
assert source.count(anchor)==1
diagnostic=r'''#include <dirent.h>
static void samgr_waitpoints_031(pid_t child)
{
    char path[256], value[16384];
    const char *files[] = {"wchan", "syscall", "stack", "maps", "status"};
    for (unsigned i=0; i<sizeof(files)/sizeof(files[0]); ++i) {
        snprintf(path,sizeof(path),"/proc/%ld/%s",(long)child,files[i]);
        errno=0; int n=text(path,value,sizeof(value));
        dprintf(1,"SELINUX031_PROC path=%s count=%d errno=%d\n%s\n",path,n,errno,n>0?value:"");
    }
    snprintf(path,sizeof(path),"/proc/%ld/task",(long)child);
    DIR *tasks=opendir(path);
    if (!tasks) { dprintf(1,"SELINUX031_TASKS errno=%d\n",errno); return; }
    struct dirent *entry; unsigned count=0;
    while ((entry=readdir(tasks)) && count<12) {
        if (entry->d_name[0]=='.') continue;
        char *end; long tid=strtol(entry->d_name,&end,10);
        if (*end || tid<=0) continue;
        ++count;
        for (unsigned i=0; i<3; ++i) {
            snprintf(path,sizeof(path),"/proc/%ld/task/%ld/%s",(long)child,tid,files[i]);
            errno=0; int n=text(path,value,sizeof(value));
            dprintf(1,"SELINUX031_THREAD path=%s count=%d errno=%d\n%s\n",path,n,errno,n>0?value:"");
        }
    }
    closedir(tasks);
}
'''
source=source.replace(anchor,diagnostic+'\n'+anchor)
anchor='    int ping_ok = !exited && samgr_ping_030();'
assert source.count(anchor)==1
source=source.replace(anchor,'    if (!exited) samgr_waitpoints_031(child);\n'+anchor)
source=source.replace('SELINUX030_','SELINUX031_')
payload='source='+repr(source)+'\n'+parent['payload'][parent['payload'].index('\nfrom pathlib import Path')+1:]
payload=payload.replace('baremetal-sdk-samgr-exec-030','baremetal-sdk-samgr-exec-031')
compile(payload,'samgr-exec031-preparation','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)
