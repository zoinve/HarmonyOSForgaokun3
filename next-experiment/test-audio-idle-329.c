/* Local transport regression only; no hardware is accessed. */
#define main audio316_program_main
#include "native-audio-server-316.c"
#undef main
#include <assert.h>
#include <sys/wait.h>

int main(void)
{
    int pair[2];assert(!socketpair(AF_UNIX,SOCK_STREAM,0,pair));
    struct timeval timeout={.tv_usec=100000};
    assert(!setsockopt(pair[0],SOL_SOCKET,SO_RCVTIMEO,&timeout,sizeof(timeout)));
    pid_t child=fork();assert(child>=0);
    if (!child) {
        close(pair[0]);usleep(3500000);
        struct audio315_request request={AUDIO315_POSITION,0};
        _exit(audio315_send(pair[1],&request,sizeof(request))?1:0);
    }
    close(pair[1]);struct audio315_request request;
    assert(!request329(pair[0],&request));
    assert(request.operation==AUDIO315_POSITION && !request.bytes);
    assert(request329(pair[0],&request)==-EPIPE);
    close(pair[0]);int status;assert(waitpid(child,&status,0)==child);
    assert(WIFEXITED(status) && !WEXITSTATUS(status));
    assert(!socketpair(AF_UNIX,SOCK_STREAM,0,pair));
    assert(!setsockopt(pair[0],SOL_SOCKET,SO_RCVTIMEO,&timeout,sizeof(timeout)));
    unsigned char partial=1;assert(write(pair[1],&partial,1)==1);
    int result=request329(pair[0],&request);
    assert(result==-EAGAIN || result==-EWOULDBLOCK);
    stopping=1;assert(request329(pair[0],&request)==-ECANCELED);
    close(pair[0]);close(pair[1]);
    puts("AUDIO329_IDLE passed=1 idle_over_three_seconds=1 partial_request_bounded=1 hardware_acceptance=0");
    return 0;
}
