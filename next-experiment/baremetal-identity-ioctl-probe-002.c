/* Isolated initramfs/QEMU regression, never run against a live HarmonyOS instance. */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <grp.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mount.h>
#include <sys/reboot.h>
#include <sys/stat.h>
#include <sys/wait.h>
#include <unistd.h>
#include <linux/android/binder.h>

struct feature_set { uint64_t value; };
struct token_pair { uint64_t sender, first, reserved[2]; };
struct sender_info { struct token_pair tokens; uint64_t pid; };
struct add_permission { uint32_t token, permissions[64]; };
struct permission_bit { uint32_t token, opcode; uint8_t granted; uint8_t padding[3]; };
_Static_assert(sizeof(struct token_pair)==32,"token ABI");
_Static_assert(sizeof(struct sender_info)==40,"sender ABI");
_Static_assert(sizeof(struct add_permission)==260,"permission payload");
_Static_assert(sizeof(struct permission_bit)==12,"permission bit ABI");
#define SELF_GET _IOR('A',1,uint64_t)
#define SELF_SET _IOW('A',2,uint64_t)
#define FIRST_GET _IOR('A',3,uint64_t)
#define FIRST_SET _IOW('A',4,uint64_t)
#define PERM_ADD _IOW('A',5,uint64_t)
#define PERM_REMOVE _IOW('A',6,uint64_t)
#define PERM_GET _IOR('A',7,uint64_t)
#define PERM_SET _IOW('A',8,uint64_t)
#define FEATURES _IOWR('b',30,struct feature_set)
#define TOKENS _IOWR('b',31,struct token_pair)
#define SENDER _IOWR('b',32,struct sender_info)
static unsigned checks;
static void require(int condition,const char *label)
{
    if (!condition) { printf("IDENTITY002_FAIL %s errno=%d\n",label,errno); fflush(stdout); reboot(RB_POWER_OFF); _exit(1); }
    ++checks;
}
static void denied(int fd,unsigned long request,void *data,int expected,const char *label)
{
    errno=0;int result=ioctl(fd,request,data);require(result==-1&&errno==expected,label);
}
static int child_status(pid_t pid)
{
    int status;return waitpid(pid,&status,0)==pid&&WIFEXITED(status)&&WEXITSTATUS(status)==0;
}
static void become(uid_t uid,gid_t supplementary)
{
    if (setgroups(supplementary?1:0,supplementary?&supplementary:NULL)||setgid(uid)||setuid(uid)) _exit(90);
}
#define CHILD_CHECK(condition) do { if (!(condition)) _exit(91); } while (0)

int main(void)
{
    if (getpid()!=1) { fputs("Requires isolated PID 1\n",stderr);return 77; }
    setbuf(stdout,NULL);
    require(mount("proc","/proc","proc",MS_NOSUID|MS_NODEV|MS_NOEXEC,NULL)==0,"proc mount");
    char cmdline[4096]={0};int c=open("/proc/cmdline",O_RDONLY);require(c>=0,"cmdline open");
    ssize_t n=read(c,cmdline,sizeof(cmdline)-1);close(c);
    require(n>0&&strstr(cmdline,"harmony.identity_test=1"),"explicit isolated-test opt-in");
    require(mount("sysfs","/sys","sysfs",MS_NOSUID|MS_NODEV|MS_NOEXEC,NULL)==0,"sys mount");
    char model[128]={0};c=open("/sys/firmware/devicetree/base/model",O_RDONLY);require(c>=0,"model open");
    n=read(c,model,sizeof(model)-1);close(c);
    require(n>0&&strstr(model,"dummy-virt"),"QEMU virt only, not physical board");
    require(mount("devtmpfs","/dev","devtmpfs",MS_NOSUID,NULL)==0,"dev mount");
    int fd=open("/dev/access_token_id",O_RDWR);require(fd>=0,"real access token device");
    require(chown("/dev/access_token_id",3020,77)==0,"test inode owner");
    uint64_t value=0x1122334455667788ULL,out=0;
    require(ioctl(fd,SELF_SET,&value)==0,"root sets own test token");
    require(ioctl(fd,SELF_GET,&out)==0&&out==value,"real 64-bit self roundtrip");
    uint64_t first=0x8877665544332211ULL;
    require(ioctl(fd,FIRST_SET,&first)==0,"root sets test first token");
    require(ioctl(fd,FIRST_GET,&out)==0&&out==first,"first roundtrip");
    denied(fd,SELF_SET,(void *)1,EFAULT,"invalid user pointer");
    denied(fd,SELF_GET,NULL,EINVAL,"null user pointer");
    denied(fd,_IO('T',1),&out,EINVAL,"wrong magic");
    for(unsigned i=9;i<=25;i++)denied(fd,_IOR('A',i,uint64_t),&out,EOPNOTSUPP,"unsupported command fails honestly");
    pid_t pid=fork();require(pid>=0,"fork denial child");
    if(!pid) {
        become(1001,0);
        CHILD_CHECK(ioctl(fd,SELF_GET,&out)==0&&out==value);
        out=12;errno=0;CHILD_CHECK(ioctl(fd,SELF_SET,&out)==-1&&errno==EPERM);
        errno=0;CHILD_CHECK(ioctl(fd,FIRST_GET,&out)==-1&&errno==EPERM);
        errno=0;CHILD_CHECK(ioctl(fd,FIRST_SET,&out)==-1&&errno==EPERM);
        struct add_permission add={.token=0x5a000001};errno=0;
        CHILD_CHECK(ioctl(fd,PERM_ADD,&add)==-1&&errno==EPERM);_exit(0);
    }
    require(child_status(pid),"unprivileged denial and fork inheritance");
    pid=fork();require(pid>=0,"fork group child");
    if(!pid) { become(1001,77);out=0;CHILD_CHECK(ioctl(fd,FIRST_GET,&out)==0&&out==first);out=77;CHILD_CHECK(ioctl(fd,FIRST_SET,&out)==0);_exit(0); }
    require(child_status(pid),"supplementary group first-caller authorization");
    require(ioctl(fd,FIRST_GET,&out)==0&&out==first,"child change does not mutate parent token");
    struct add_permission add={.token=0x5a000001,.permissions={1}};
    denied(fd,PERM_ADD,&add,EPERM,"root is not permission manager");
    pid=fork();require(pid>=0,"fork manager child");
    if(!pid) {
        become(3020,0);CHILD_CHECK(ioctl(fd,PERM_ADD,&add)==0);
        struct permission_bit bit={.token=add.token,.opcode=31,.granted=1};
        CHILD_CHECK(ioctl(fd,PERM_SET,&bit)==0);CHILD_CHECK(ioctl(fd,PERM_GET,&bit)==1);
        bit.granted=0;CHILD_CHECK(ioctl(fd,PERM_SET,&bit)==0);CHILD_CHECK(ioctl(fd,PERM_GET,&bit)==0);
        bit.opcode=2048;errno=0;CHILD_CHECK(ioctl(fd,PERM_GET,&bit)==-1&&errno==EINVAL);
        CHILD_CHECK(ioctl(fd,PERM_REMOVE,&add.token)==0);errno=0;bit.opcode=0;
        CHILD_CHECK(ioctl(fd,PERM_GET,&bit)==-1&&errno==ENODATA);_exit(0);
    }
    require(child_status(pid),"manager actual permission-bit operations");
    mkdir("/dev/binderfs",0700);
    require(mount("binder","/dev/binderfs","binder",MS_NOSUID|MS_NOEXEC,NULL)==0,"binderfs mount");
    int ctl=open("/dev/binderfs/binder-control",O_RDWR);require(ctl>=0,"binder control");
    /* BINDER_CTL_ADD lives in binderfs.h, independent of identity-extension UAPI. */
    struct { char name[256]; uint32_t major,minor; } device={.name="identity002"};
    require(ioctl(ctl,_IOWR('b',1,device),&device)==0,"isolated binder device");close(ctl);
    int binder=open("/dev/binderfs/identity002",O_RDWR);require(binder>=0,"binder open");
    struct binder_version version={0};require(ioctl(binder,BINDER_VERSION,&version)==0&&version.protocol_version==8,"Binder protocol 8");
    struct feature_set features={0};require(ioctl(binder,FEATURES,&features)==0&&features.value==5,"observed feature bits only");
    struct token_pair tokens;memset(&tokens,0xa5,sizeof(tokens));require(ioctl(binder,TOKENS,&tokens)==0,"access-token ioctl");
    require(tokens.sender==0&&tokens.first==0&&tokens.reserved[0]==0&&tokens.reserved[1]==0,"new Binder thread has no fabricated caller");
    struct sender_info sender;memset(&sender,0xa5,sizeof(sender));require(ioctl(binder,SENDER,&sender)==0,"sender-info ioctl");
    require(sender.tokens.sender==0&&sender.tokens.first==0&&sender.tokens.reserved[0]==0&&sender.tokens.reserved[1]==0&&sender.pid==0,"zero reserved and initial sender fields");
    close(binder);close(fd);
    printf("IDENTITY002_PASS checks=%u transactions_not_tested=1 desktop_not_tested=1\n",checks);
    reboot(RB_POWER_OFF);return 1;
}
