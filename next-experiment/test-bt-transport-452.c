#define _GNU_SOURCE
#include <assert.h>
#include <errno.h>
#include <poll.h>
#include <pthread.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

static int interrupted_send,interrupted_recv,interrupted_poll;
static int inject_send,inject_recv,inject_poll;
static int inject_send_fd=-1,inject_recv_fd=-1;
static ssize_t fixture_send(int fd,const void *data,size_t n,int flags)
{
    if(inject_send&&(inject_send_fd<0||inject_send_fd==fd)){
        inject_send=0;interrupted_send++;errno=EINTR;return -1;
    }
    return send(fd,data,n,flags);
}
static ssize_t fixture_recv(int fd,void *data,size_t n,int flags)
{
    if(inject_recv&&(inject_recv_fd<0||inject_recv_fd==fd)){
        inject_recv=0;interrupted_recv++;errno=EINTR;return -1;
    }
    return recv(fd,data,n,flags);
}
static int fixture_poll(struct pollfd *fds,nfds_t n,int ms)
{
    if(inject_poll){inject_poll=0;interrupted_poll++;errno=EINTR;return -1;}
    return poll(fds,n,ms);
}
#define send fixture_send
#define recv fixture_recv
#define poll fixture_poll
#define main broker451_main
#include "broker.c"
#undef main
#undef poll
#undef recv
#undef send

struct session {int client,hci;};
static void *run_pump(void *arg)
{struct session *s=arg;pump(s->client,s->hci);return NULL;}
static void sockets(int stream[2],int controller[2])
{
    assert(!socketpair(AF_UNIX,SOCK_STREAM,0,stream));
    assert(!socketpair(AF_UNIX,SOCK_SEQPACKET,0,controller));
    struct timeval timeout={.tv_sec=2};
    assert(!setsockopt(controller[1],SOL_SOCKET,SO_RCVTIMEO,&timeout,sizeof(timeout)));
    assert(!setsockopt(stream[1],SOL_SOCKET,SO_RCVTIMEO,&timeout,sizeof(timeout)));
}
static void close_session(int stream[2],int controller[2])
{for(unsigned i=0;i<2;++i){if(stream[i]>=0)close(stream[i]);close(controller[i]);}}
static void buffered_close(void)
{
    int s[2],h[2];sockets(s,h);
    const unsigned char packets[]={1,3,0x0c,0,2,1,0,2,0,0xa5,0x5a};
    assert(send(s[1],packets,sizeof(packets),0)==sizeof(packets));
    close(s[1]);s[1]=-1;
    struct pollfd ready={s[0],POLLIN,0};assert(poll(&ready,1,0)==1);
    assert((ready.revents&POLLHUP)&&(ready.revents&POLLIN));
    inject_send=inject_recv=inject_poll=1;pump(s[0],h[0]);
    unsigned char actual[32];
    assert(recv(h[1],actual,sizeof(actual),0)==4&&!memcmp(actual,packets,4));
    assert(recv(h[1],actual,sizeof(actual),0)==7&&!memcmp(actual,packets+4,7));
    assert(interrupted_send==1&&interrupted_recv==1&&interrupted_poll==1);
    close_session(s,h);
}
static void bidirectional(void)
{
    int s[2],h[2];sockets(s,h);struct session session={s[0],h[0]};pthread_t thread;
    inject_send_fd=s[0];inject_recv_fd=h[0];inject_send=inject_recv=inject_poll=1;
    assert(!pthread_create(&thread,NULL,run_pump,&session));
    const unsigned char command[]={1,3,0x0c,0};unsigned char actual[32];
    assert(send(s[1],command,2,0)==2);
    assert(send(s[1],command+2,2,0)==2);
    assert(recv(h[1],actual,sizeof(actual),0)==sizeof(command));
    assert(!memcmp(command,actual,sizeof(command)));
    const unsigned char event[]={4,0x0e,4,1,3,0x0c,0};
    assert(send(h[1],event,sizeof(event),0)==sizeof(event));
    assert(recv(s[1],actual,sizeof(event),MSG_WAITALL)==sizeof(event));
    assert(!memcmp(event,actual,sizeof(event)));
    assert(!shutdown(s[1],SHUT_WR));assert(!pthread_join(thread,NULL));
    assert(interrupted_send==2&&interrupted_recv==2&&interrupted_poll==2);
    close_session(s,h);
}
int main(void)
{
    signal(SIGPIPE,SIG_IGN);alarm(12);
    buffered_close();bidirectional();
    puts("BT452 buffered_hangup_fragmented_coalesced_exact_bytes_eintr=pass physical_hci=0");
}
