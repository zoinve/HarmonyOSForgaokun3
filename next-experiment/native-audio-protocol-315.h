#ifndef NATIVE_AUDIO_PROTOCOL_315_H
#define NATIVE_AUDIO_PROTOCOL_315_H
#include <errno.h>
#include <stdint.h>
#include <sys/socket.h>
#include <unistd.h>

#define AUDIO315_MAGIC 0x41333135U
#define AUDIO315_VERSION 2U
#define AUDIO363_SPEAKER 0U
#define AUDIO363_HEADPHONES 1U
#define AUDIO315_MAX_BYTES 65536U
#define AUDIO315_SOCKET "/vendor/lib64/harmony-graphics/native-audio315.sock"
enum { AUDIO315_WRITE=1, AUDIO315_POSITION, AUDIO315_FLUSH, AUDIO315_DRAIN, AUDIO315_CLOSE };
struct audio315_config {uint32_t magic,version,rate,channels,format,route;};
struct audio315_request {uint32_t operation,bytes;};
struct audio315_reply {
    uint32_t magic,version;
    int32_t error;
    uint32_t accepted_bytes,rate,channels,frame_bytes,period_frames,buffer_frames,route;
    uint64_t submitted_frames,played_frames,monotonic_ns;
    int64_t delay_frames;
};
_Static_assert(sizeof(struct audio315_config)==24,"audio config wire ABI");
_Static_assert(sizeof(struct audio315_reply)==72,"audio reply wire ABI");

static inline int audio315_send(int fd,const void *data,size_t size)
{
    const unsigned char *p=data;
    while (size) {
        ssize_t sent=send(fd,p,size,MSG_NOSIGNAL);
        if (sent<0 && errno==EINTR) continue;
        if (sent<=0) return -1;
        p+=sent; size-=(size_t)sent;
    }
    return 0;
}
static inline int audio315_receive(int fd,void *data,size_t size)
{
    unsigned char *p=data;
    while (size) {
        ssize_t got=recv(fd,p,size,0);
        if (got<0 && errno==EINTR) continue;
        if (got<=0) return -1;
        p+=got; size-=(size_t)got;
    }
    return 0;
}
#endif
