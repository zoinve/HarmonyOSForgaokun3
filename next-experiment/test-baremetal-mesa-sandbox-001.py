"""Execute real sandbox isolation with a static CPU-only payload, never a simulated GPU pass."""
from pathlib import Path
import subprocess

source=Path(__file__).with_name('baremetal-mesa-launcher-001.c').read_text()
payload='source='+repr(source)+'\n'+r'''
from pathlib import Path
import os,subprocess,tempfile,json
assert os.geteuid()==0,'Namespace/device fixture needs local root; do not bypass a failure'
probe=r"""
#define _GNU_SOURCE
#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <dirent.h>
#include <sys/prctl.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <unistd.h>
int main(void) {
    assert(getpid()==1 && getuid()==65534 && geteuid()==65534 && getgid()==65534 && getgroups(0,0)==0);
    assert(prctl(PR_GET_NO_NEW_PRIVS,0,0,0,0)==1);
    FILE *f=fopen("/proc/self/status","r"); assert(f); char line[512]; unsigned found=0;
    while(fgets(line,sizeof(line),f)) {
        if (!strncmp(line,"CapEff:",7)||!strncmp(line,"CapPrm:",7)||!strncmp(line,"CapInh:",7)||!strncmp(line,"CapBnd:",7)||!strncmp(line,"CapAmb:",7)) {
            unsigned long long value=1;assert(sscanf(line+7,"%llx",&value)==1 && value==0);++found;
        }
    }
    fclose(f);assert(found==5);
    assert(access("/dev/dri/card0",F_OK) && access("/dev/nvme0n1",F_OK) && access("/dev/input",F_OK));
    assert(access("/mnt/harmony-lab",F_OK) && access("/boot/efi",F_OK));
    struct stat device; assert(!stat("/dev/dri/renderD128",&device) && S_ISCHR(device.st_mode) && major(device.st_rdev)==226 && minor(device.st_rdev)==128);
    FILE *bad=fopen("/app/forbidden-write","w"); assert(!bad);
    FILE *good=fopen("/tmp/own-write","w"); assert(good);fputs("test-only",good);fclose(good);
    DIR *net=opendir("/sys/class/net"); assert(net); struct dirent *entry;
    while((entry=readdir(net))) if(entry->d_name[0]!='.') assert(!strcmp(entry->d_name,"lo"));
    closedir(net);
    puts("CPU_ONLY_SANDBOX_PASS namespaces_uid_capabilities_readonly_and_device_view GPU_NOT_TESTED=1");
    return 0;
}
"""
driver=r"""
#undef main
int main(void) {
    umask(0); require(!mkdir(MESA_ROOT,0700),"test exclusive mountpoint");
    require(!unshare(CLONE_NEWNS|CLONE_NEWNET|CLONE_NEWPID),"test namespaces");
    require(!mount(NULL,"/",NULL,MS_PRIVATE|MS_REC,NULL),"test private propagation");
    pid_t child=fork(); require(child>=0,"test namespace child"); if (!child) sandbox();
    int status; require(waitpid(child,&status,0)==child,"test wait");
    require(!umount2(MESA_ROOT,MNT_DETACH) && !rmdir(MESA_ROOT),"test cleanup");
    return WIFEXITED(status)?WEXITSTATUS(status):128+WTERMSIG(status);
}
"""
with tempfile.TemporaryDirectory(prefix='mesa-sandbox001-',dir='/home/zoinve/harmony-virgl-883') as directory:
    p=Path(directory);(p/'bundle/lib').mkdir(parents=True);(p/'probe.c').write_text(probe)
    subprocess.run(['cc','-static','-O2','-Wall','-Wextra','-Werror',str(p/'probe.c'),'-o',str(p/'bundle/lib/ld-musl-aarch64.so.1')],check=True)
    render=p/'render-fixture';os.mknod(render,0o20660,os.makedev(226,128))
    defines=''.join('#define '+name+' '+json.dumps(str(path))+'\n' for name,path in [('MESA_ROOT',p/'root'),('MESA_BUNDLE',p/'bundle'),('MESA_RENDER',render)])
    (p/'sandbox.c').write_text(defines+'#define main original_main\n'+source+driver)
    subprocess.run(['cc','-O2','-Wall','-Wextra','-Werror',str(p/'sandbox.c'),'-o',str(p/'test')],check=True)
    subprocess.run([str(p/'test')],check=True,timeout=15)
'''
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','-u','root','--','python3','-'],input=payload,text=True,timeout=50)
    raise SystemExit(r.returncode)
