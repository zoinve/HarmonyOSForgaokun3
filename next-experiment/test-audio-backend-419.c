/* Generated server with ALSA doubles; never loads libasound or opens hardware. */
#define main server_main419
#include "server.c"
#undef main
#include <assert.h>

static unsigned step419,mode419,waits419;
static long read419(snd_pcm_t *pcm,void *data,unsigned long frames)
{
    assert(pcm==(snd_pcm_t *)(uintptr_t)1);
    if(mode419==1)return -EIO;
    if(mode419==2)return (long)frames+1;
    if(mode419==3)return 1;
    if(step419++==0)return -EAGAIN;
    if(step419==2){assert(frames>=1);memset(data,0x31,4);return 1;}
    return -EIO;
}
static int wait419(snd_pcm_t *pcm,int timeout)
{assert(pcm==(snd_pcm_t *)(uintptr_t)1&&timeout==100);waits419++;return 1;}
static int delay419(snd_pcm_t *pcm,long *delay)
{assert(pcm==(snd_pcm_t *)(uintptr_t)1);*delay=2;return 0;}
int main(void)
{
    alsa.snd_pcm_readi=read419;alsa.snd_pcm_wait=wait419;alsa.snd_pcm_delay=delay419;
    struct stream316 stream={.pcm=(snd_pcm_t *)(uintptr_t)1,.route=AUDIO412_MIC,.period=48,.buffer=480};
    unsigned char bytes[12];memset(bytes,0xa5,sizeof(bytes));unsigned accepted=99;
    assert(read411(&stream,bytes,8,&accepted)==-EIO&&accepted==4);
    assert(waits419==1&&stream.submitted==1&&stream.captured==1);
    assert(bytes[0]==0x31&&bytes[3]==0x31&&bytes[4]==0xa5&&bytes[11]==0xa5);
    mode419=1;accepted=99;
    assert(read411(&stream,bytes,8,&accepted)==-EIO&&!accepted&&stream.captured==1);
    mode419=2;assert(read411(&stream,bytes,8,&accepted)==-EIO&&!accepted);
    mode419=3;stream.submitted=UINT64_MAX;
    assert(read411(&stream,bytes,8,&accepted)==-EOVERFLOW&&!accepted);
    stream.submitted=3;stream.captured=UINT64_MAX;
    assert(read411(&stream,bytes,8,&accepted)==-EOVERFLOW&&!accepted);
    stream.captured=3;stopping=1;
    assert(read411(&stream,bytes,8,&accepted)==-EINTR&&!accepted);
    stopping=0;
    struct audio315_reply reply=reply316(&stream,0,4);
    assert(!reply.error&&reply.submitted_frames==3&&reply.played_frames==5&&reply.delay_frames==2&&reply.monotonic_ns);
    stream.buffer=1;assert(reply316(&stream,0,0).error==-EIO);
    stream.buffer=480;stream.submitted=UINT64_MAX;assert(reply316(&stream,0,0).error==-EIO);

    /* Fill both bounded worker slots with incomplete configs, then shut down. */
    pthread_attr_t attributes;assert(!pthread_attr_init(&attributes));
    assert(!pthread_attr_setdetachstate(&attributes,PTHREAD_CREATE_DETACHED));
    int first[2],second[2],third[2];
    assert(!socketpair(AF_UNIX,SOCK_STREAM,0,first));
    assert(!socketpair(AF_UNIX,SOCK_STREAM,0,second));
    assert(!socketpair(AF_UNIX,SOCK_STREAM,0,third));
    assert(!dispatch411(first[0],&attributes)&&!dispatch411(second[0],&attributes));
    assert(dispatch411(third[0],&attributes)==-EBUSY);
    close(third[0]);close(third[1]);
    uint64_t start=now316();stopping=1;
    pthread_mutex_lock(&workers411_lock);
    for(unsigned i=0;i<2;++i){assert(workers411[i].active);assert(!shutdown(workers411[i].fd,SHUT_RDWR));}
    struct timespec deadline;assert(!clock_gettime(CLOCK_REALTIME,&deadline));deadline.tv_sec+=2;
    while(workers411[0].active||workers411[1].active)
        assert(!pthread_cond_timedwait(&workers411_done,&workers411_lock,&deadline));
    pthread_mutex_unlock(&workers411_lock);
    assert(now316()-start<2000000000ULL);
    close(first[1]);close(second[1]);pthread_attr_destroy(&attributes);
    puts("AUDIO419 real_read_accounting_worker_bound_shutdown=pass physical_capture=0");
    return 0;
}
