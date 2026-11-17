#define _GNU_SOURCE
#include <stdio.h>
#include <fcntl.h>
#define open unit376_open
#define fopen unit376_fopen
#include "native-audio-jack-376.c"
#include <assert.h>

static unsigned calls377;
static int present377=1,index377,fail377,regular377;
static unsigned switches377;
static int device377(const char *path,int flags,...)
{
    unsigned index;
    assert(sscanf(path,"/dev/input/event%u",&index)==1);
    assert((flags&O_ACCMODE)==O_RDONLY&&(flags&O_NOFOLLOW));
    ++calls377;
    if(index!=0&&(index!=10||!present377)){errno=ENOENT;return -1;}
    index377=(int)index;return open376_next("/dev/null",flags);
}
static int stat377(int fd,struct stat *state)
{
    int result=fstat(fd,state);
    if(!result&&regular377)state->st_mode=S_IFREG|0600;
    return result;
}
static int ioctl377(int fd,unsigned long request,void *opaque)
{
    (void)fd;unsigned char *data=opaque;
    if(request==EVIOCGNAME(256)){
        strcpy((char *)data,index377==10?"SC8280XP-HUAWEI-GAOKUN3 Headset Jack":"not a jack");return 1;
    }
    if(request==EVIOCGBIT(0,8)){data[0]=1U<<EV_SW;return 8;}
    if(request==EVIOCGBIT(EV_SW,8)){data[0]=(1U<<SW_HEADPHONE_INSERT)|(1U<<SW_MICROPHONE_INSERT);return 8;}
    assert(request==EVIOCGSW(8));
    if(fail377){errno=EIO;return -1;}
    data[0]=(unsigned char)switches377;return 8;
}
int main(void)
{
    pthread_once(&once376,load376);assert(open376_next&&fopen376_next);
    io376.open=device377;io376.stat=stat377;io376.ioctl=ioctl377;
    assert(!caller376((void *)main));
    calls377=0;int fd=open("/dev/null",O_RDONLY);assert(fd>=0&&!calls377);close(fd);
    FILE *file=fopen("/dev/null","r");assert(file&&!calls377);fclose(file);
    unsigned char switches[8]={0};int index=-1;
    fd=jack376(switches,&index);assert(fd>=0&&index==10&&!switches[0]);close(fd);
    fd=input376(O_RDONLY);assert(fd>=0&&!(fcntl(fd,F_GETFL)&O_NONBLOCK));close(fd);
    fd=input376(O_RDONLY|O_NONBLOCK);assert(fd>=0&&(fcntl(fd,F_GETFL)&O_NONBLOCK));close(fd);
    calls377=0;assert(input376(O_WRONLY)<0&&errno==EACCES&&!calls377);
    assert(input376(O_RDONLY|O_TRUNC)<0&&errno==EACCES&&!calls377);
    unsigned states[]={0,1U<<SW_HEADPHONE_INSERT,(1U<<SW_HEADPHONE_INSERT)|(1U<<SW_MICROPHONE_INSERT)};
    const char *expected[]={"0\n","2\n","1\n"};
    for(unsigned i=0;i<3;++i){
        switches377=states[i];file=snapshot376("r");assert(file);
        char bytes[3]={0};assert(fread(bytes,1,2,file)==2&&!strcmp(bytes,expected[i]));
        assert((fcntl(fileno(file),F_GETFL)&O_ACCMODE)==O_RDONLY);
        assert(write(fileno(file),"x",1)<0);
        assert((fcntl(fileno(file),F_GET_SEALS)&F_SEAL_WRITE)!=0);
        fclose(file);
    }
    switches377=1U<<SW_MICROPHONE_INSERT;assert(!snapshot376("r")&&errno==EAGAIN);
    switches377=1U<<SW_LINEOUT_INSERT;assert(!snapshot376("r")&&errno==ENOTSUP);
    assert(!snapshot376("w")&&errno==EACCES);
    fail377=1;assert(!snapshot376("r")&&errno==EIO);fail377=0;
    regular377=1;assert(!snapshot376("r")&&errno==ENODEV);regular377=0;
    present377=0;assert(!snapshot376("r")&&errno==ENODEV);
    puts("AUDIO377_UNIT passed=1 real_state_translation_cases=3 unknown_state_is_error=1 unrelated_callers_unchanged=1 input_injected=0 hardware_acceptance=0");
    return 0;
}
