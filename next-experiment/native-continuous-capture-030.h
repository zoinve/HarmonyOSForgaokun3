#ifndef NATIVE_CONTINUOUS_CAPTURE_030_H
#define NATIVE_CONTINUOUS_CAPTURE_030_H
#include <errno.h>
#include <poll.h>
#include <stddef.h>
#include <unistd.h>
/* Returns 0 at EOF, 1 at capacity, -1 on an actual read/write/sync error.
   No target process, watchdog or reboot control. Sync even during idle periods. */
static int capture_stream030(int input,int output,size_t limit)
{
    size_t total=0;
    unsigned char data[16384];
    while(total<limit){
        struct pollfd p={.fd=input,.events=POLLIN};
        int ready=poll(&p,1,2000);
        if(ready<0){if(errno==EINTR)continue;return -1;}
        if(fsync(output))return -1;
        if(!ready)continue;
        size_t count=limit-total;if(count>sizeof(data))count=sizeof(data);
        ssize_t n=read(input,data,count);
        if(n<0){if(errno==EINTR)continue;return -1;}
        if(!n)return fsync(output)?-1:0;
        size_t done=0;
        while(done<(size_t)n){
            ssize_t w=write(output,data+done,(size_t)n-done);
            if(w<0 && errno==EINTR)continue;
            if(w<=0)return -1;
            done+=(size_t)w;
        }
        total+=(size_t)n;
    }
    return fsync(output)?-1:1;
}
#endif
