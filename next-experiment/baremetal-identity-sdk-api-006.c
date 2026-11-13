/* Test the original SDK DSO, not reimplemented API wrappers. QEMU only. */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <grp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

static unsigned checks;
static void check(int condition,const char *name)
{
    if(!condition) { printf("SDK006_FAIL %s errno=%d\n",name,errno);fflush(stdout);exit(1); }
    ++checks;
}
static int contains(const char *path,const char *needle)
{
    char data[4096]={0};int fd=open(path,O_RDONLY);if(fd<0)return 0;
    ssize_t size=read(fd,data,sizeof(data)-1);close(fd);return size>0&&strstr(data,needle)!=NULL;
}
static int child_ok(pid_t pid)
{
    int status;return waitpid(pid,&status,0)==pid&&WIFEXITED(status)&&WEXITSTATUS(status)==0;
}
int main(void)
{
    if(getuid()!=0||!contains("/proc/cmdline","harmony.identity_test=1")||
        !contains("/sys/firmware/devicetree/base/model","dummy-virt"))return 77;
    setbuf(stdout,NULL);
    void *lib=dlopen("libtokensetproc_shared.z.so",RTLD_NOW|RTLD_LOCAL);
    if(!lib)fprintf(stderr,"SDK006_DLOPEN %s\n",dlerror());
    check(lib!=NULL,"load unmodified original SDK library");
    uint64_t (*get_self)(void)=dlsym(lib,"GetSelfTokenID");
    uint64_t (*get_first)(void)=dlsym(lib,"GetFirstCallerTokenID");
    int (*set_self)(uint64_t)=dlsym(lib,"SetSelfTokenID");
    int (*set_first)(uint64_t)=dlsym(lib,"SetFirstCallerTokenID");
    int (*version)(uint32_t *)=dlsym(lib,"SpmGetVersion");
    int (*parent)(uint32_t,uint64_t *)=dlsym(lib,"GetParentHapTokenID");
    check(get_self&&get_first&&set_self&&set_first&&version&&parent,"resolve real exported SDK APIs");
    check(get_self()==0x1122334455667788ULL&&get_first()==0x8877665544332211ULL,"SDK reads identities inherited across exec");
    const uint64_t self=0x5000000000000500ULL,first=0x6000000000000600ULL;
    check(set_self(self)==0&&get_self()==self,"original SDK self-token roundtrip");
    check(set_first(first)==0&&get_first()==first,"original SDK first-caller roundtrip");
    uint32_t supported=0xffffffff;
    int error=version(&supported);
    printf("SDK006_SPM version_result=%d version=%u\n",error,supported);
    check(error==EOPNOTSUPP&&supported==0,"original SDK reports unsupported SPM as version zero, not false success");
    uint64_t parent_token=0xa5a5a5a5a5a5a5a5ULL;
    error=parent(123,&parent_token);
    check(error==EOPNOTSUPP&&parent_token==0xa5a5a5a5a5a5a5a5ULL,"unsupported parent-token API preserves output and returns real error");
    pid_t pid=fork();check(pid>=0,"fork SDK denial test");
    if(!pid) {
        check(setgroups(0,NULL)==0&&setgid(1001)==0&&setuid(1001)==0,"SDK test drops privileges");
        check(get_self()==self,"unprivileged original SDK reads inherited own token");
        errno=0;check(set_self(7)==-1&&errno==EPERM,"original SDK self-token mutation denied");
        check(get_first()==0,"original SDK denied first-caller read returns no identity");
        errno=0;check(set_first(7)==-1&&errno==EPERM,"original SDK first-caller mutation denied");
        _exit(0);
    }
    check(child_ok(pid),"SDK denial child succeeds");
    pid=fork();check(pid>=0,"fork SDK authorized supplementary-group test");
    if(!pid) {
        gid_t group=77;
        check(setgroups(1,&group)==0&&setgid(1001)==0&&setuid(1001)==0,"SDK test sets authorized supplementary group");
        check(get_first()==first,"original SDK group-authorized first-caller read");
        check(set_first(first+1)==0&&get_first()==first+1,"original SDK group-authorized first-caller change");
        _exit(0);
    }
    check(child_ok(pid),"SDK authorized group child succeeds");
    check(get_self()==self&&get_first()==first,"SDK child changes do not mutate parent identities");
    check(dlclose(lib)==0,"close original SDK library");
    printf("SDK006_PASS checks=%u original_library=1 spm_unsupported_honestly=1 services_not_tested=1\n",checks);
    return 0;
}
