/* Test doubles exercise error/accounting paths, never hardware acceptance. */
#define main audio316_program_main
#include "native-audio-server-316.c"
#undef main
#include <assert.h>

static int pending=1,draining=1;
static long delay318=2;
static long write318(snd_pcm_t *pcm,const void *data,unsigned long frames)
{
    (void)pcm;(void)data;
    if (pending) {pending=0;return -EAGAIN;}
    return (long)(frames>2?2:frames);
}
static long broken318(snd_pcm_t *pcm,const void *data,unsigned long frames)
{(void)pcm;(void)data;(void)frames;return -EPIPE;}
static int wait318(snd_pcm_t *pcm,int timeout) {(void)pcm;(void)timeout;return 1;}
static int delay318_get(snd_pcm_t *pcm,long *delay) {(void)pcm;*delay=delay318;return 0;}
static int drain318(snd_pcm_t *pcm) {(void)pcm;if (draining) {draining=0;return -EAGAIN;}return 0;}

int main(void)
{
    alsa.snd_pcm_writei=write318;alsa.snd_pcm_wait=wait318;
    alsa.snd_pcm_delay=delay318_get;alsa.snd_pcm_drain=drain318;
    struct stream316 stream={.pcm=(snd_pcm_t *)(uintptr_t)1,.period=2,.buffer=4};
    unsigned char samples[16]={0};unsigned accepted=0;
    assert(!write316(&stream,samples,sizeof(samples),&accepted));
    assert(accepted==16 && stream.submitted==4);
    struct audio315_reply reply=reply316(&stream,0,accepted);
    assert(!reply.error && reply.accepted_bytes==16 && reply.played_frames==2 && reply.monotonic_ns);
    delay318=5;reply=reply316(&stream,0,0);assert(reply.error==-EIO);
    delay318=2;alsa.snd_pcm_writei=broken318;
    assert(write316(&stream,samples,sizeof(samples),&accepted)==-EPIPE && accepted==0 && stream.submitted==4);
    reply=reply316(&stream,-EPIPE,0);assert(reply.error==-EPIPE && reply.accepted_bytes==0);
    assert(!drain316(&stream));reply=reply316(&stream,0,0);
    assert(!reply.error && reply.played_frames==4 && reply.delay_frames==0);
    int pair[2];assert(!socketpair(AF_UNIX,SOCK_STREAM,0,pair));
    struct audio315_config invalid={0};
    assert(!audio315_send(pair[0],&invalid,sizeof(invalid)));
    client316(pair[1]);
    assert(!audio315_receive(pair[0],&reply,sizeof(reply)));
    assert(reply.error==-ENOTSUP && reply.accepted_bytes==0 && reply.submitted_frames==0);
    close(pair[1]);assert(audio315_send(pair[0],samples,sizeof(samples))==-1);close(pair[0]);
    puts("AUDIO318_SELFTEST passed=1 test_doubles_only=1 hardware_acceptance=0");
    return 0;
}
