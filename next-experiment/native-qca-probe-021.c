#define _GNU_SOURCE
#include <errno.h>
#include <poll.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <time.h>
#include <unistd.h>

static int reset_reply(const unsigned char *p,size_t n)
{
    if(n<7 || p[0]!=4 || p[1]!=14 || p[2]<4 || n<(size_t)p[2]+3 || p[4]!=3 || p[5]!=12)return 0;
    return p[6]==0?1:-1;
}
int main(void)
{
    /* Only called by the opt-in native diagnostic init, not by Ubuntu. */
    unsigned char command[]={1,3,12,0},buf[260];
    struct {uint16_t family,device,channel;} address={31,0,1};
    int fd=-1;
    for(unsigned attempt=0;attempt<15;++attempt){
        fd=socket(31,SOCK_RAW|SOCK_CLOEXEC,1);
        if(fd<0)break;
        if(!bind(fd,(struct sockaddr *)&address,sizeof(address)))break;
        int saved=errno;close(fd);fd=-1;
        dprintf(1,"NATIVE_QCA021 bind_attempt=%u errno=%d\n",attempt,saved);
        if(saved!=EBUSY && saved!=ENODEV)break;
        usleep(500000);
    }
    if(fd<0){dprintf(1,"NATIVE_QCA021 unavailable errno=%d\n",errno);return 1;}
    if(send(fd,command,sizeof(command),0)!=(ssize_t)sizeof(command)){perror("HCI reset send");close(fd);return 2;}
    for(unsigned attempt=0;attempt<10;++attempt){
        struct pollfd item={.fd=fd,.events=POLLIN};
        int ready=poll(&item,1,500);
        if(ready<0 && errno==EINTR){--attempt;continue;}
        if(ready<=0)continue;
        ssize_t n=recv(fd,buf,sizeof(buf),0);
        if(n<=0)break;
        dprintf(1,"NATIVE_QCA021 received bytes=%zd packet=",n);
        for(ssize_t i=0;i<n;++i)dprintf(1,"%02x",buf[i]);
        dprintf(1,"\n");
        int result=reset_reply(buf,(size_t)n);
        if(result){close(fd);dprintf(1,"NATIVE_QCA021 real_reset_success=%d status=%u\n",result==1,buf[6]);return result==1?0:3;}
    }
    close(fd);dprintf(1,"NATIVE_QCA021 reset_timeout=1\n");return 4;
}
