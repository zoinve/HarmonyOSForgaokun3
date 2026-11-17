#ifndef COMMERCIAL_SAFETY_010_H
#define COMMERCIAL_SAFETY_010_H
#include <errno.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>
/* Eight GiB is a capacity, not an immediate allocation. Keep at least three
 * GiB available beyond it for the kernel, services and non-data RAM state. */
static inline int commercial_ram_budget010(unsigned long long total,unsigned long long available)
{
    const unsigned long long gib=1024ULL*1024*1024;
    return total>=15*gib && available>=11*gib;
}
static inline long long commercial_millis010(void)
{
    struct timespec now;
    if(clock_gettime(CLOCK_MONOTONIC,&now))return -1;
    return (long long)now.tv_sec*1000+now.tv_nsec/1000000;
}
/* The caller remains in control even if its worker blocks in kernel I/O.
 * SIGKILL cannot itself interrupt uninterruptible I/O: never wait for that
 * child synchronously on the timeout path. A wedged kernel is not recoverable
 * by this userspace mechanism. */
static inline int commercial_bounded010(void (*task)(void *),void *argument,unsigned timeout_ms)
{
    long long start=commercial_millis010();
    if(start<0 || !task || !timeout_ms)return 125;
    pid_t child=fork();
    if(child<0)return 125;
    if(!child){task(argument);_exit(0);}
    for(;;){
        int status=0;pid_t got=waitpid(child,&status,WNOHANG);
        if(got==child)return WIFEXITED(status)?WEXITSTATUS(status):125;
        if(got<0 && errno!=EINTR){kill(child,SIGKILL);return 125;}
        long long now=commercial_millis010();
        if(now<0 || now-start>=timeout_ms){
            kill(child,SIGKILL);
            (void)waitpid(child,&status,WNOHANG);
            return 124;
        }
        struct timespec pause={0,5000000};
        (void)nanosleep(&pause,NULL);
    }
}
#endif
