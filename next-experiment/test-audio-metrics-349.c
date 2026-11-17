/* Real write-accounting paths with local ALSA doubles, not hardware acceptance. */
#define main audio316_program_main
#include "native-audio-server-316.c"
#undef main
#include <assert.h>
static unsigned calls;
static long partial349(snd_pcm_t *pcm,const void *data,unsigned long frames)
{(void)pcm;(void)data;(void)frames;return calls++==0?2:-EPIPE;}
static long full349(snd_pcm_t *pcm,const void *data,unsigned long frames)
{(void)pcm;(void)data;return (long)frames;}
int main(void)
{
    struct stream316 stream={.pcm=(snd_pcm_t *)(uintptr_t)1};
    unsigned char data[]={0,0,0,0,0,0x80,0xff,0x7f,1,0,0,0,0,0,0,0};
    alsa.snd_pcm_writei=partial349;unsigned accepted=0;
    assert(write316(&stream,data,sizeof(data),&accepted)==-EPIPE);
    assert(accepted==8&&stream.submitted==2&&stream.metrics.accepted_frames==2);
    assert(stream.metrics.nonzero_frames==1&&stream.metrics.peak_abs==32768);
    assert(write316(&stream,data,sizeof(data),&accepted)==-EPIPE&&accepted==0);
    assert(stream.metrics.accepted_frames==2&&stream.metrics.nonzero_frames==1);
    alsa.snd_pcm_writei=full349;
    assert(!write316(&stream,data+8,8,&accepted)&&accepted==8);
    assert(stream.metrics.accepted_frames==4&&stream.metrics.nonzero_frames==2);
    assert(stream.metrics.peak_abs==32768);
    puts("AUDIO349_TEST passed=1 unaccepted_samples_not_counted=1 hardware_acceptance=0");
    return 0;
}
