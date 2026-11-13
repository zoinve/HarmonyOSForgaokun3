/* Diagnostic-only reads. No token setters, permission mutation, or persistent state. */
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

struct feature_set { uint64_t value; };
struct token_pair { uint64_t sender,first,reserved[2]; };
struct sender_info { struct token_pair tokens; uint64_t pid; };
_Static_assert(sizeof(struct token_pair)==32,"token ABI");
_Static_assert(sizeof(struct sender_info)==40,"sender ABI");

int main(void)
{
    char cmdline[4096]={0};struct utsname kernel;
    int c=open("/proc/cmdline",O_RDONLY|O_CLOEXEC);
    ssize_t n=c<0?-1:read(c,cmdline,sizeof(cmdline)-2);if(c>=0)close(c);
    if(n>0){for(ssize_t i=0;i<n;i++)if(cmdline[i]=='\n'||cmdline[i]=='\t')cmdline[i]=' ';cmdline[n]=' ';cmdline[n+1]=0;}
    if(uname(&kernel)||strcmp(kernel.release,"7.1.0-rc3-gaokun3-el2")||n<=0||
       (strncmp(cmdline,"harmony.diag=1 ",15)&&!strstr(cmdline," harmony.diag=1 "))||geteuid()!=0) {
        fputs("Read-only ABI probe requires diagnostic kernel and opt-in\n",stderr);return 77;
    }
    int fd=-1,ctl=-1,binder=-1,mounted=0,created=0,rc=1;
    const char *directory="/run/identity-read-001";
#define CHECK(condition,label) do { if(!(condition)){fprintf(stderr,"NATIVE_IDENTITY_READ001_FAIL %s errno=%d\n",label,errno);goto done;} } while(0)
    fd=open("/dev/access_token_id",O_RDONLY|O_CLOEXEC);CHECK(fd>=0,"open token device");
    uint64_t own=0,first=0;
    CHECK(ioctl(fd,_IOR('A',1,uint64_t),&own)==0,"read own token");
    CHECK(ioctl(fd,_IOR('A',3,uint64_t),&first)==0,"read first-caller token");
    uint32_t version=0xa5a5a5a5;errno=0;
    CHECK(ioctl(fd,_IOR('A',25,uint32_t),&version)==-1&&errno==EOPNOTSUPP&&version==0xa5a5a5a5,"unsupported SPM command remains an error");
    CHECK(mkdir(directory,0700)==0,"exclusive RAM mountpoint");created=1;
    CHECK(mount("binder",directory,"binder",MS_NOSUID|MS_NOEXEC,NULL)==0,"private binderfs mount");mounted=1;
    ctl=open("/run/identity-read-001/binder-control",O_RDWR|O_CLOEXEC);CHECK(ctl>=0,"binder control");
    struct { char name[256];uint32_t major,minor; } device={.name="identity-read-001"};
    CHECK(ioctl(ctl,_IOWR('b',1,device),&device)==0,"create private ephemeral binder device");
    binder=open("/run/identity-read-001/identity-read-001",O_RDWR|O_CLOEXEC);CHECK(binder>=0,"private Binder open");
    struct binder_version protocol={0};
    CHECK(ioctl(binder,BINDER_VERSION,&protocol)==0&&protocol.protocol_version==8,"Binder protocol");
    struct feature_set features={0};
    CHECK(ioctl(binder,_IOWR('b',30,struct feature_set),&features)==0&&features.value==5,"exact supported feature bits");
    struct token_pair tokens;memset(&tokens,0xa5,sizeof(tokens));
    CHECK(ioctl(binder,_IOWR('b',31,struct token_pair),&tokens)==0,"token-pair ABI");
    CHECK(!tokens.sender&&!tokens.first&&!tokens.reserved[0]&&!tokens.reserved[1],"fresh Binder thread identity is not fabricated");
    struct sender_info sender;memset(&sender,0xa5,sizeof(sender));
    CHECK(ioctl(binder,_IOWR('b',32,struct sender_info),&sender)==0,"sender-info ABI");
    CHECK(!sender.tokens.sender&&!sender.tokens.first&&!sender.tokens.reserved[0]&&!sender.tokens.reserved[1]&&!sender.pid,"fresh sender fields and reserved bytes");
    rc=0;
done:
    if(binder>=0)close(binder);
    if(ctl>=0)close(ctl);
    if(fd>=0)close(fd);
    if(mounted&&umount(directory)){perror("private binderfs unmount");rc=1;}
    if(created&&rmdir(directory)){perror("private binderfs mountpoint removal");rc=1;}
    if(!rc)printf("NATIVE_IDENTITY_READ001_PASS protocol=8 features=5 task_self=%016llx task_first=%016llx tokens_modified=0 permissions_modified=0 transactions_not_tested=1 desktop_not_tested=1\n",(unsigned long long)own,(unsigned long long)first);
    return rc;
}
