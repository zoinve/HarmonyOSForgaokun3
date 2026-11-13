/* Target-only HCI_USER <-> H4 stream bridge. No command or event translation. */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <sys/un.h>
#include <unistd.h>

struct hci_address {sa_family_t family;unsigned short device,channel;};
static int h4_length(const unsigned char *p,size_t n)
{
    if(!n)return 0;
    switch(p[0]){
    case 1:return n<4?0:4+p[3];
    case 2:return n<5?0:5+p[3]+((int)p[4]<<8);
    case 3:return n<4?0:4+p[3];
    case 5:return n<5?0:5+p[3]+(((int)p[4]&63)<<8);
    default:return -1;
    }
}
static int write_all(int fd,const unsigned char *p,size_t n)
{
    while(n){ssize_t k=send(fd,p,n,MSG_NOSIGNAL);if(k<0 && errno==EINTR)continue;
        if(k<=0)return -1;
        p+=k;n-=(size_t)k;
    }return 0;
}
static int open_controller(void)
{
    for(unsigned i=0;i<20;++i){
        int fd=socket(31,SOCK_RAW|SOCK_CLOEXEC,1);
        if(fd<0)return -1;
        struct hci_address address={.family=31,.device=0,.channel=1};
        if(!bind(fd,(struct sockaddr *)&address,sizeof(address)))return fd;
        int saved=errno;close(fd);errno=saved;
        if(saved!=EBUSY && saved!=ENODEV)return -1;
        usleep(250000);
    }return -1;
}
static void pump(int client,int hci)
{
    unsigned char queued[131080],packet[65540];size_t count=0;unsigned logs=0;
    for(;;){
        struct pollfd p[2]={{client,POLLIN,0},{hci,POLLIN,0}};
        int rc=poll(p,2,2000);if(rc<0 && errno==EINTR)continue;
        if(rc<0 || (p[0].revents&(POLLERR|POLLHUP|POLLNVAL)) || (p[1].revents&(POLLERR|POLLHUP|POLLNVAL)))break;
        if(p[0].revents&POLLIN){
            ssize_t n=recv(client,queued+count,sizeof(queued)-count,0);if(n<=0)break;
            count+=(size_t)n;
            while(count){
                int size=h4_length(queued,count);if(size<0)return;
                if(!size || (size_t)size>count)break;
                if(logs++<128 && queued[0]==1)dprintf(1,"NATIVE_QCA022 command opcode=%04x bytes=%d\n",queued[1]|((unsigned)queued[2]<<8),size);
                if(send(hci,queued,(size_t)size,MSG_NOSIGNAL)!=size)return;
                count-=(size_t)size;memmove(queued,queued+size,count);
            }
            if(count==sizeof(queued))break;
        }
        if(p[1].revents&POLLIN){
            ssize_t n=recv(hci,packet,sizeof(packet),0);if(n<=0)break;
            if(logs++<128 && n>=7 && packet[0]==4 && packet[1]==14)
                dprintf(1,"NATIVE_QCA022 completion opcode=%04x status=%u bytes=%zd\n",packet[4]|((unsigned)packet[5]<<8),packet[6],n);
            if(write_all(client,packet,(size_t)n))break;
        }
    }
}
int main(int argc,char **argv)
{
    if(argc!=2 || getuid()!=0){fprintf(stderr,"requires target root and exact socket path\n");return 77;}
    const char *path=argv[1];
    if(strcmp(path,"/native-target/native-bt-broker.sock"))return 77;
    signal(SIGPIPE,SIG_IGN);
    int server=socket(AF_UNIX,SOCK_STREAM|SOCK_CLOEXEC,0);if(server<0)return 1;
    struct sockaddr_un address={.sun_family=AF_UNIX};
    if(strlen(path)>=sizeof(address.sun_path))return 1;
    strcpy(address.sun_path,path);
    /* Never unlink an existing endpoint belonging to another run. */
    if(bind(server,(struct sockaddr *)&address,sizeof(address)) || chmod(path,0600) || chown(path,3021,3021) || listen(server,4))return 1;
    dprintf(1,"NATIVE_QCA022 broker_listening=1 allowed_uid=3021 controller=0\n");
    for(;;){
        int client=accept4(server,NULL,NULL,SOCK_CLOEXEC);if(client<0){if(errno==EINTR)continue;return 1;}
        struct ucred peer;socklen_t len=sizeof(peer);
        if(getsockopt(client,SOL_SOCKET,SO_PEERCRED,&peer,&len) || peer.uid!=3021){close(client);continue;}
        int hci=open_controller();int saved=errno;unsigned char ack=hci<0?1:0;
        struct timeval timeout={.tv_sec=2};setsockopt(client,SOL_SOCKET,SO_SNDTIMEO,&timeout,sizeof(timeout));
        dprintf(1,"NATIVE_QCA022 real_channel_open=%d peer_uid=%u errno=%d\n",hci>=0,(unsigned)peer.uid,hci<0?saved:0);
        if(!write_all(client,&ack,1) && hci>=0)pump(client,hci);
        close(client);if(hci>=0)close(hci);
        dprintf(1,"NATIVE_QCA022 real_channel_closed=1\n");
    }
}
