#ifndef LIVE_DEBUG_DISCOVERY_159_H
#define LIVE_DEBUG_DISCOVERY_159_H
#include <arpa/inet.h>
#include <errno.h>
#include <net/if.h>
#include <poll.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <time.h>
#include <unistd.h>

#define DISCOVERY159_PORT 22259
#define DISCOVERY159_QUERY_BYTES 128
#define DISCOVERY159_PREFIX "HARMONY_DIAG_DISCOVER_159 "

/* Discovery is untrusted routing information. SSH authenticates the endpoint. */
static int discovery159_nonce(const char *packet, size_t size, char nonce[33])
{
    const size_t prefix = sizeof(DISCOVERY159_PREFIX) - 1;
    if (size != DISCOVERY159_QUERY_BYTES || memcmp(packet,DISCOVERY159_PREFIX,prefix)) return -1;
    for (size_t i = 0; i < 32; ++i) {
        char c = packet[prefix + i];
        if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f'))) return -1;
    }
    for (size_t i = prefix + 32; i < size - 1; ++i) if (packet[i] != ' ') return -1;
    if (packet[size - 1] != '\n') return -1;
    memcpy(nonce,packet + prefix,32);
    nonce[32] = 0;
    return 0;
}

static int discovery159_peer(const struct sockaddr_in *peer)
{
    unsigned ip = ntohl(peer->sin_addr.s_addr);
    return peer->sin_family == AF_INET && ntohs(peer->sin_port) >= 1024 &&
        (ip == 0xc0a80ac9U || ip == 0xc0a80af8U);
}

static int discovery159_open(const char *interface)
{
    size_t length = strlen(interface);
    if (!length || length >= IFNAMSIZ || !if_nametoindex(interface)) return -1;
    int fd = socket(AF_INET,SOCK_DGRAM | SOCK_CLOEXEC | SOCK_NONBLOCK,0);
    if (fd < 0) return -1;
    int on = 1;
    struct sockaddr_in local = {.sin_family=AF_INET,.sin_port=htons(DISCOVERY159_PORT),.sin_addr={.s_addr=htonl(INADDR_ANY)}};
    if (setsockopt(fd,SOL_SOCKET,SO_BINDTODEVICE,interface,length + 1) ||
        setsockopt(fd,IPPROTO_IP,IP_PKTINFO,&on,sizeof(on)) ||
        bind(fd,(struct sockaddr *)&local,sizeof(local))) {
        close(fd); return -1;
    }
    return fd;
}

/* One bounded datagram per call; no log strings or remote commands are returned. */
static int discovery159_step(int fd, unsigned interface_index, const char *address,
                             unsigned *remaining, time_t *last_reply)
{
    char packet[DISCOVERY159_QUERY_BYTES], nonce[33];
    struct sockaddr_in peer = {0};
    union { struct cmsghdr aligned; char bytes[CMSG_SPACE(sizeof(struct in_pktinfo))]; } control;
    struct iovec vector = {.iov_base=packet,.iov_len=sizeof(packet)};
    struct msghdr message = {.msg_name=&peer,.msg_namelen=sizeof(peer),.msg_iov=&vector,.msg_iovlen=1,
        .msg_control=control.bytes,.msg_controllen=sizeof(control.bytes)};
    ssize_t size = recvmsg(fd,&message,MSG_DONTWAIT | MSG_TRUNC);
    if (size < 0) return errno == EAGAIN || errno == EWOULDBLOCK || errno == EINTR ? 0 : -1;
    if (message.msg_flags & (MSG_TRUNC | MSG_CTRUNC) || !*remaining ||
        !discovery159_peer(&peer) || discovery159_nonce(packet,(size_t)size,nonce)) return 0;
    struct in_addr actual;
    if (inet_pton(AF_INET,address,&actual) != 1) return -1;
    int right_interface = 0;
    for (struct cmsghdr *item = CMSG_FIRSTHDR(&message); item; item = CMSG_NXTHDR(&message,item)) {
        if (item->cmsg_level != IPPROTO_IP || item->cmsg_type != IP_PKTINFO ||
            item->cmsg_len != CMSG_LEN(sizeof(struct in_pktinfo))) continue;
        struct in_pktinfo info;
        memcpy(&info,CMSG_DATA(item),sizeof(info));
        unsigned destination = ntohl(info.ipi_addr.s_addr);
        if ((unsigned)info.ipi_ifindex == interface_index && info.ipi_spec_dst.s_addr == actual.s_addr &&
            (destination == ntohl(actual.s_addr) || destination == 0xc0a80affU)) right_interface = 1;
    }
    struct timespec now;
    if (!right_interface || clock_gettime(CLOCK_MONOTONIC,&now)) return 0;
    if (*last_reply >= now.tv_sec) return 0;
    char reply[DISCOVERY159_QUERY_BYTES];
    int length = snprintf(reply,sizeof(reply),"HARMONY_DIAG_ENDPOINT_159 %s %s 22257\n",nonce,address);
    if (length < 0 || length >= DISCOVERY159_QUERY_BYTES) return -1;
    --*remaining;
    *last_reply = now.tv_sec;
    return sendto(fd,reply,(size_t)length,0,(struct sockaddr *)&peer,sizeof(peer)) == length ? 1 : -1;
}
#endif
