/* Adapt legacy policy paths to real evdev jack switches; never inject input. */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <linux/input.h>
#include <pthread.h>
#include <stdarg.h>
#include <stdatomic.h>
#include <stdio.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

struct jack376_ops {
    int (*open)(const char *,int,...);
    int (*stat)(int,struct stat *);
    int (*ioctl)(int,unsigned long,void *);
    int (*close)(int);
};
static int ioctl376(int fd,unsigned long request,void *value)
{return ioctl(fd,request,value);}
static struct jack376_ops io376={NULL,fstat,ioctl376,close};
static int (*open376_next)(const char *,int,...);
static FILE *(*fopen376_next)(const char *,const char *);
static pthread_once_t once376=PTHREAD_ONCE_INIT;
static atomic_uint trace376_count;

static void load376(void)
{
    *(void **)(&open376_next)=dlsym(RTLD_NEXT,"open");
    *(void **)(&fopen376_next)=dlsym(RTLD_NEXT,"fopen");
    io376.open=open376_next;
}
static int caller376(void *address)
{
    Dl_info info;
    if(!dladdr(address,&info)||!info.dli_fname)return 0;
    const char *base=strrchr(info.dli_fname,'/');
    return !strcmp(base?base+1:info.dli_fname,"libaudio_policy_service.z.so");
}
static void trace376(const char *operation,int value,int error)
{
    int saved=errno;
    if(atomic_fetch_add_explicit(&trace376_count,1,memory_order_relaxed)<32&&open376_next){
        int fd=open376_next("/vendor/lib64/harmony-graphics/audio-jack376.trace",
            O_WRONLY|O_APPEND|O_CLOEXEC|O_NOFOLLOW);
        struct stat state;
        if(fd>=0&&!fstat(fd,&state)&&S_ISREG(state.st_mode)&&state.st_uid==1041&&
           (state.st_mode&0777)==0600&&state.st_nlink==1&&state.st_size<8192)
            dprintf(fd,"AUDIO376_%s value=%d errno=%d real_evdev=1 input_injected=0 microphone_recorded=0\n",
                operation,value,error);
        if(fd>=0)close(fd);
    }
    errno=saved;
}
static int bit376(const unsigned char *bits,unsigned bit)
{return !!(bits[bit/8]&(1U<<(bit%8)));}

/* The returned descriptor is the real device, subject to ordinary permissions. */
static int jack376(unsigned char *switches,int *index)
{
    for(unsigned i=0;i<64;++i){
        char path[64],name[256]={0};
        snprintf(path,sizeof(path),"/dev/input/event%u",i);
        int fd=io376.open(path,O_RDONLY|O_NONBLOCK|O_CLOEXEC|O_NOFOLLOW);
        if(fd<0)continue;
        struct stat state;
        if(io376.stat(fd,&state)||!S_ISCHR(state.st_mode)||
           io376.ioctl(fd,EVIOCGNAME(sizeof(name)),name)<0){io376.close(fd);continue;}
        name[sizeof(name)-1]=0;
        if(strcmp(name,"SC8280XP-HUAWEI-GAOKUN3 Headset Jack")){io376.close(fd);continue;}
        unsigned char types[8]={0},caps[8]={0};
        int result=io376.ioctl(fd,EVIOCGBIT(0,sizeof(types)),types);
        if(result>=0&&!bit376(types,EV_SW)){errno=ENOTSUP;result=-1;}
        if(result>=0)result=io376.ioctl(fd,EVIOCGBIT(EV_SW,sizeof(caps)),caps);
        if(result>=0&&(!bit376(caps,SW_HEADPHONE_INSERT)||!bit376(caps,SW_MICROPHONE_INSERT))){
            errno=ENOTSUP;result=-1;
        }
        if(result>=0)result=io376.ioctl(fd,EVIOCGSW(8),switches);
        if(result<0){int error=errno;io376.close(fd);errno=error;return -1;}
        *index=(int)i;return fd;
    }
    errno=ENODEV;return -1;
}
static int state376(const unsigned char *switches)
{
    int headphone=bit376(switches,SW_HEADPHONE_INSERT);
    int microphone=bit376(switches,SW_MICROPHONE_INSERT);
    if(microphone&&!headphone){errno=EAGAIN;return -1;}
    if(bit376(switches,SW_LINEOUT_INSERT)){errno=ENOTSUP;return -1;}
    return !headphone?'0':microphone?'1':'2';
}
static int input376(int flags)
{
    if((flags&O_ACCMODE)!=O_RDONLY||(flags&(O_CREAT|O_TRUNC))){errno=EACCES;return -1;}
    unsigned char switches[8]={0};int index=-1;
    int fd=jack376(switches,&index);
    if(fd<0){trace376("INPUT",-1,errno);return -1;}
    /* Match the caller's blocking mode without changing the underlying device. */
    int status=fcntl(fd,F_GETFL);
    if(status<0||fcntl(fd,F_SETFL,(status&~O_NONBLOCK)|(flags&O_NONBLOCK))<0){
        int error=errno;io376.close(fd);errno=error;trace376("INPUT",-1,error);return -1;
    }
    trace376("INPUT",index,0);return fd;
}
static FILE *snapshot376(const char *mode)
{
    if(strcmp(mode,"r")&&strcmp(mode,"re")){errno=EACCES;return NULL;}
    unsigned char switches[8]={0};int index=-1;
    int device=jack376(switches,&index);
    if(device<0){trace376("STATE",-1,errno);return NULL;}
    io376.close(device);
    int value=state376(switches);
    if(value<0){trace376("STATE",-1,errno);return NULL;}
    int fd=memfd_create("audio-jack376",MFD_CLOEXEC|MFD_ALLOW_SEALING);
    if(fd<0)return NULL;
    char contents[2]={(char)value,'\n'};
    int error=0;
    ssize_t written=write(fd,contents,sizeof(contents));
    if(written<0)error=errno;
    else if(written!=sizeof(contents))error=EIO;
    else if(fcntl(fd,F_ADD_SEALS,F_SEAL_WRITE|F_SEAL_GROW|F_SEAL_SHRINK|F_SEAL_SEAL)<0)error=errno;
    char path[64];snprintf(path,sizeof(path),"/proc/self/fd/%d",fd);
    int readonly=error?-1:open376_next(path,O_RDONLY|O_CLOEXEC);
    if(readonly<0&&!error)error=errno;
    close(fd);
    if(error){errno=error;trace376("STATE",-1,error);return NULL;}
    FILE *file=fdopen(readonly,mode);
    if(!file){error=errno;close(readonly);errno=error;return NULL;}
    trace376("STATE",value-'0',0);return file;
}

__attribute__((visibility("default"))) int open(const char *path,int flags,...)
{
    mode_t mode=0;
    int needs_mode=flags&O_CREAT;
#ifdef O_TMPFILE
    needs_mode|=(flags&O_TMPFILE)==O_TMPFILE;
#endif
    if(needs_mode){va_list args;va_start(args,flags);mode=(mode_t)va_arg(args,int);va_end(args);}
    pthread_once(&once376,load376);
    if(!open376_next){errno=ENOSYS;return -1;}
    if(caller376(__builtin_return_address(0))){
        if(!strcmp(path,"/dev/input/event1"))return input376(flags);
        if(!strcmp(path,"/dev/input/event2")||!strcmp(path,"/dev/input/event3")||
           !strcmp(path,"/dev/input/event4")){errno=ENOENT;return -1;}
    }
    return open376_next(path,flags,mode);
}
__attribute__((visibility("default"))) FILE *fopen(const char *path,const char *mode)
{
    pthread_once(&once376,load376);
    if(!fopen376_next||!open376_next){errno=ENOSYS;return NULL;}
    if(!strcmp(path,"/sys/class/switch/h2w/state")&&caller376(__builtin_return_address(0)))
        return snapshot376(mode);
    return fopen376_next(path,mode);
}
