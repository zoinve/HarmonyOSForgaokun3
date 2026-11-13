"""Fix namespace root rebasing; retain candidate 002 diagnostics and target files."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
previous=runpy.run_path(str(base/'build-native-original-graphics-boot-002.py'))
inner,outer=previous['inner'],previous['outer']
old='''    if(mount(NULL,"/",NULL,MS_REC|MS_PRIVATE,NULL) || chdir("/native-target") || chroot(".") || chdir("/"))
        _exit(90);'''
new='''    if(mount(NULL,"/",NULL,MS_REC|MS_PRIVATE,NULL))_exit(90);
    /* OPEN_TREE_NAMESPACE (Linux API bit 1): namespace / must equal target /.
     * Original init enters mount namespaces; setns resets root to namespace /.
     * Chroot alone therefore exposes the diagnostic root again. No fallback.
     */
    int rooted=(int)syscall(SYS_open_tree,AT_FDCWD,"/native-target",2|O_CLOEXEC|AT_RECURSIVE);
    if(rooted<0 || setns(rooted,CLONE_NEWNS) || chdir("/")){
        dprintf(1,"NATIVE_ROOT_NAMESPACE003 failed errno=%d\\n",errno);_exit(90);
    }
    close(rooted);
    dprintf(1,"NATIVE_ROOT_NAMESPACE003 rooted=1 chroot_fallback=0\\n");'''
assert outer.count(old)==1
outer=outer.replace(old,new).replace('native-original-002-%s','native-original-003-%s')
outer='#include <sys/syscall.h>\n'+outer
payload=previous['payload']
offset=payload.index('from pathlib import Path\nimport gzip,hashlib')
payload='inner='+repr(inner)+'\nouter='+repr(outer)+'\n'+payload[offset:]
payload=payload.replace('native-original-graphics-boot-002','native-original-graphics-boot-003')
if __name__=='__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
