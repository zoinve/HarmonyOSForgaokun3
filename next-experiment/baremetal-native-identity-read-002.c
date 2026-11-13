/* Diagnostic reads only: no policy loading, token setters, or permission mutation. */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <sys/utsname.h>
#include <unistd.h>
#include <linux/android/binder.h>

struct token_pair { uint64_t sender,first,reserved[2]; };
struct sender_info { struct token_pair tokens; uint64_t pid; };
_Static_assert(sizeof(struct token_pair)==32,"token ABI");
_Static_assert(sizeof(struct sender_info)==40,"sender ABI");

static int option(const char *line,const char *wanted)
{
    size_t length=strlen(wanted);
    while(*line) {
        line+=strspn(line," \t\r\n");
        size_t word=strcspn(line," \t\r\n");
        if(word==length&&!memcmp(line,wanted,length))return 1;
        line+=word;
    }
    return 0;
}

int main(void)
{
    struct utsname kernel;char cmdline[4096]={0};
    int c=open("/proc/cmdline",O_RDONLY|O_CLOEXEC);
    ssize_t n=c<0?-1:read(c,cmdline,sizeof(cmdline)-1);if(c>=0)close(c);
    if(uname(&kernel)||strcmp(kernel.release,"7.1.0-rc3-gaokun3-el2")||
       n<=0||n>=(ssize_t)sizeof(cmdline)-1||geteuid()!=0||
       !option(cmdline,"harmony.diag=1")||!option(cmdline,"enforcing=1")) {
        fputs("Read-only ABI probe requires diagnostic kernel and opt-in enforcing=1\n",stderr);
        return 77;
    }
    int token=-1,binder=-1,enforce=-1,created=0,mounted=0,rc=1;
    uint64_t own=0,first=0;
    const char *directory="/run/identity-read-002";
#define CHECK(condition,label) do { if(!(condition)){fprintf(stderr,"NATIVE_IDENTITY_READ002_FAIL %s errno=%d\n",label,errno);goto done;} } while(0)
    CHECK(!mkdir(directory,0700),"exclusive RAM SELinuxfs mountpoint");created=1;
    CHECK(!mount("selinuxfs",directory,"selinuxfs",MS_RDONLY|MS_NODEV|MS_NOSUID|MS_NOEXEC,NULL),
          "active SELinux read-only filesystem");mounted=1;
    enforce=open("/run/identity-read-002/enforce",O_RDONLY|O_CLOEXEC);
    CHECK(enforce>=0,"read enforcing state");
    char state[8]={0};ssize_t length=read(enforce,state,sizeof(state));
    CHECK((length==1&&state[0]=='1')||(length==2&&state[0]=='1'&&state[1]=='\n'),
          "actual SELinux enforcing state must be one");
    token=open("/dev/access_token_id",O_RDONLY|O_CLOEXEC);CHECK(token>=0,"open actual token device");
    CHECK(!ioctl(token,_IOR('A',1,uint64_t),&own),"read own token");
    CHECK(!ioctl(token,_IOR('A',3,uint64_t),&first),"read first-caller token");
    uint32_t version=0xa5a5a5a5;errno=0;
    CHECK(ioctl(token,_IOR('A',25,uint32_t),&version)==-1&&errno==EOPNOTSUPP&&version==0xa5a5a5a5,
          "unsupported SPM remains an error before policy load");
    binder=open("/dev/binder",O_RDWR|O_CLOEXEC);CHECK(binder>=0,"open traditional Binder device");
    struct binder_version protocol={0};uint64_t features=0;
    CHECK(!ioctl(binder,BINDER_VERSION,&protocol)&&protocol.protocol_version==8,"Binder protocol");
    CHECK(!ioctl(binder,_IOWR('b',30,uint64_t),&features)&&features==5,"exact supported Binder features");
    struct token_pair pair;memset(&pair,0xa5,sizeof(pair));
    CHECK(!ioctl(binder,_IOWR('b',31,struct token_pair),&pair),"token-pair read ABI");
    CHECK(!pair.sender&&!pair.first&&!pair.reserved[0]&&!pair.reserved[1],"fresh thread identity and reserved bytes");
    struct sender_info sender;memset(&sender,0xa5,sizeof(sender));
    CHECK(!ioctl(binder,_IOWR('b',32,struct sender_info),&sender),"sender read ABI");
    CHECK(!sender.tokens.sender&&!sender.tokens.first&&!sender.tokens.reserved[0]&&
          !sender.tokens.reserved[1]&&!sender.pid,"fresh sender identity and reserved bytes");
    rc=0;
done:
    if(binder>=0)close(binder);
    if(token>=0)close(token);
    if(enforce>=0)close(enforce);
    if(mounted&&umount(directory)){perror("read-only SELinuxfs unmount");rc=1;}
    if(created&&rmdir(directory)){perror("RAM mountpoint removal");rc=1;}
    if(!rc)printf("NATIVE_IDENTITY_READ002_PASS protocol=8 features=5 legacy_binder=1 selinux_active=1 enforcing=1 task_self=%016llx task_first=%016llx tokens_modified=0 permissions_modified=0 policy_loaded_by_probe=0 transactions_not_tested=1 desktop_not_tested=1\n",
                  (unsigned long long)own,(unsigned long long)first);
    return rc;
}
