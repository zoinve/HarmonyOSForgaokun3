/* Private bounded diagnostic protocol: exactly one linear ARGB buffer FD and one fence FD. */
#ifndef BAREMETAL_BUFFER_IPC_001_H
#define BAREMETAL_BUFFER_IPC_001_H
#include <stdint.h>
#include <sys/socket.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <string.h>

struct buffer_packet001 {
    uint32_t magic,width,height,stride,format,offset;
    uint64_t modifier;
};
_Static_assert(sizeof(struct buffer_packet001)==32,"fixed private packet layout");

static inline int buffer_packet_valid001(const struct buffer_packet001 *p)
{
    return p && p->magic==0x42464631 && p->width>0 && p->width<=4096 &&
        p->height>0 && p->height<=4096 && p->stride>=p->width*4 &&
        (uint64_t)p->stride*p->height<=256u*1024u*1024u &&
        p->format==0x34325241 && p->offset==0 && p->modifier==0;
}

static inline int buffer_send001(int socket_fd,const struct buffer_packet001 *p,const int fds[2])
{
    if(!buffer_packet_valid001(p) || !fds || fds[0]<0 || fds[1]<0) {errno=EINVAL;return -1;}
    struct iovec io={(void *)p,sizeof(*p)};
    union {struct cmsghdr align;char bytes[CMSG_SPACE(2*sizeof(int))];} control={0};
    struct msghdr message={0};message.msg_iov=&io;message.msg_iovlen=1;
    message.msg_control=control.bytes;message.msg_controllen=sizeof(control.bytes);
    struct cmsghdr *c=CMSG_FIRSTHDR(&message);
    c->cmsg_level=SOL_SOCKET;c->cmsg_type=SCM_RIGHTS;c->cmsg_len=CMSG_LEN(2*sizeof(int));
    memcpy(CMSG_DATA(c),fds,2*sizeof(int));
    ssize_t n;
    do {n=sendmsg(socket_fd,&message,MSG_NOSIGNAL);} while(n<0 && errno==EINTR);
    return n==(ssize_t)sizeof(*p)?0:-1;
}

static inline int buffer_recv001(int socket_fd,struct buffer_packet001 *out,int fds[2])
{
    if(!out || !fds) {errno=EINVAL;return -1;}
    fds[0]=fds[1]=-1;
    struct buffer_packet001 packet={0};struct iovec io={&packet,sizeof(packet)};
    union {struct cmsghdr align;char bytes[CMSG_SPACE(8*sizeof(int))];} control={0};
    struct msghdr message={0};message.msg_iov=&io;message.msg_iovlen=1;
    message.msg_control=control.bytes;message.msg_controllen=sizeof(control.bytes);
    ssize_t n;
    do {n=recvmsg(socket_fd,&message,MSG_CMSG_CLOEXEC);} while(n<0 && errno==EINTR);
    if(n<0)return -1;
    int received[8],count=0,valid=1;
    size_t position=0;
    while(position+sizeof(struct cmsghdr)<=message.msg_controllen) {
        struct cmsghdr *c=(struct cmsghdr *)(control.bytes+position);
        if(c->cmsg_len<CMSG_LEN(0) || c->cmsg_len>message.msg_controllen-position) {
            valid=0;break;
        }
        size_t bytes=c->cmsg_len-CMSG_LEN(0);
        position+=CMSG_SPACE(bytes);
        if(c->cmsg_level!=SOL_SOCKET || c->cmsg_type!=SCM_RIGHTS) {
            valid=0;continue;
        }
        if(bytes%sizeof(int))valid=0;
        for(size_t i=0;i<bytes/sizeof(int);++i) {
            int descriptor;memcpy(&descriptor,(char *)CMSG_DATA(c)+i*sizeof(int),sizeof(descriptor));
            if(count<8)received[count++]=descriptor;
            else {close(descriptor);valid=0;}
        }
    }
    valid=valid && n==(ssize_t)sizeof(packet) && !(message.msg_flags&(MSG_TRUNC|MSG_CTRUNC)) &&
        count==2 && buffer_packet_valid001(&packet);
    if(!valid) {
        for(int i=0;i<count;++i)close(received[i]);
        errno=EPROTO;return -1;
    }
    *out=packet;fds[0]=received[0];fds[1]=received[1];return 0;
}
#endif
