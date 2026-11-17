/* Bounded public-API playback probe. No capture, token changes, or direct ALSA. */
#define _POSIX_C_SOURCE 200809L
#include <ohaudio/native_audiostreambuilder.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <unistd.h>
#include <errno.h>

struct audio350_context {
    int16_t wave[1200];
    atomic_uint_fast64_t cursor,callbacks,nonzero_frames;
    atomic_uint invalid_buffers;
};
static struct audio350_context context350;

static void audio350_wave(struct audio350_context *context)
{
    for(unsigned i=0;i<1200;++i)
        context->wave[i]=(int16_t)(256.0*sin(6.283185307179586*11*i/1200));
}
static OH_AudioData_Callback_Result audio350_write(OH_AudioRenderer *renderer,void *opaque,void *buffer,int32_t bytes)
{
    (void)renderer;
    struct audio350_context *context=opaque;
    if(!context||!buffer||bytes<=0||bytes%4){
        if(context)atomic_fetch_add(&context->invalid_buffers,1);
        return AUDIO_DATA_CALLBACK_RESULT_INVALID;
    }
    unsigned frames=(unsigned)bytes/4;
    uint64_t first=atomic_fetch_add(&context->cursor,frames),nonzero=0;
    unsigned char *out=buffer;
    for(unsigned i=0;i<frames;++i){
        uint64_t position=first+i;int value=0;
        if(position>=4800&&position<14400){
            unsigned offset=(unsigned)(position-4800),fade=240;
            if(offset<fade)fade=offset;
            if(9599-offset<fade)fade=9599-offset;
            value=context->wave[offset%1200]*(int)fade/240;
        }
        if(value)++nonzero;
        uint16_t sample=(uint16_t)(int16_t)value;
        out[i*4]=out[i*4+2]=(unsigned char)sample;
        out[i*4+1]=out[i*4+3]=(unsigned char)(sample>>8);
    }
    atomic_fetch_add(&context->callbacks,1);
    atomic_fetch_add(&context->nonzero_frames,nonzero);
    return AUDIO_DATA_CALLBACK_RESULT_VALID;
}
static void audio350_sleep(unsigned milliseconds)
{
    struct timespec delay={milliseconds/1000,(long)(milliseconds%1000)*1000000L};
    while(nanosleep(&delay,&delay)&&errno==EINTR){}
}
static int audio350_step(const char *name,OH_AudioStream_Result result)
{
    dprintf(1,"AUDIO350_STEP name=%s code=%d original_service_checks=1\n",name,(int)result);
    return result!=AUDIOSTREAM_SUCCESS;
}
static int audio350_snapshot(OH_AudioRenderer *renderer,const char *stage)
{
    int64_t frames=-1,position=-1,time=-1;uint32_t underflows=0;
    int a=OH_AudioRenderer_GetFramesWritten(renderer,&frames);
    int b=OH_AudioRenderer_GetTimestamp(renderer,CLOCK_MONOTONIC,&position,&time);
    int c=OH_AudioRenderer_GetUnderflowCount(renderer,&underflows);
    dprintf(1,"AUDIO350_STATE stage=%s frames_code=%d frames=%lld timestamp_code=%d position=%lld time_ns=%lld underflow_code=%d underflows=%u audible_verified=0\n",
        stage,a,(long long)frames,b,(long long)position,(long long)time,c,underflows);
    return a!=AUDIOSTREAM_SUCCESS||b!=AUDIOSTREAM_SUCCESS||c!=AUDIOSTREAM_SUCCESS||
        frames<=0||position<0||time<=0;
}
int main(void)
{
    alarm(15);
    dprintf(1,"AUDIO350_BEGIN uid=%u gid=%u public_renderer_api=1 credentials_unmodified=1 microphone_recorded=0 tone_ms_per_start=200 source_peak=256\n",
        (unsigned)getuid(),(unsigned)getgid());
    audio350_wave(&context350);
    OH_AudioStreamBuilder *builder=NULL;OH_AudioRenderer *renderer=NULL;
    int result=1,started=0;
#define STEP(call) do{if(audio350_step(#call,(call)))goto finish;}while(0)
    STEP(OH_AudioStreamBuilder_Create(&builder,AUDIOSTREAM_TYPE_RENDERER));
    STEP(OH_AudioStreamBuilder_SetSamplingRate(builder,48000));
    STEP(OH_AudioStreamBuilder_SetChannelCount(builder,2));
    STEP(OH_AudioStreamBuilder_SetSampleFormat(builder,AUDIOSTREAM_SAMPLE_S16LE));
    STEP(OH_AudioStreamBuilder_SetEncodingType(builder,AUDIOSTREAM_ENCODING_TYPE_RAW));
    STEP(OH_AudioStreamBuilder_SetLatencyMode(builder,AUDIOSTREAM_LATENCY_MODE_NORMAL));
    STEP(OH_AudioStreamBuilder_SetRendererInfo(builder,AUDIOSTREAM_USAGE_MUSIC));
    STEP(OH_AudioStreamBuilder_SetRendererWriteDataCallback(builder,audio350_write,&context350));
    STEP(OH_AudioStreamBuilder_GenerateRenderer(builder,&renderer));
    STEP(OH_AudioRenderer_SetVolume(renderer,0.25f));
    STEP(OH_AudioRenderer_Start(renderer));started=1;
    audio350_sleep(800);
    if(audio350_snapshot(renderer,"first_running"))goto finish;
    STEP(OH_AudioRenderer_Pause(renderer));started=0;
    audio350_sleep(3500);
    atomic_store(&context350.cursor,0);
    STEP(OH_AudioRenderer_Start(renderer));started=1;
    audio350_sleep(800);
    if(audio350_snapshot(renderer,"resumed_running"))goto finish;
    STEP(OH_AudioRenderer_Stop(renderer));started=0;
    result=atomic_load(&context350.invalid_buffers)||!atomic_load(&context350.nonzero_frames);
finish:
    if(renderer){
        if(started)audio350_step("cleanup_stop",OH_AudioRenderer_Stop(renderer));
        if(audio350_step("release",OH_AudioRenderer_Release(renderer)))result=1;
    }
    if(builder&&audio350_step("builder_destroy",OH_AudioStreamBuilder_Destroy(builder)))result=1;
    dprintf(1,"AUDIO350_END result=%d callbacks=%llu source_nonzero_frames=%llu invalid_buffers=%u acoustic_output_verified=0\n",
        result,(unsigned long long)atomic_load(&context350.callbacks),
        (unsigned long long)atomic_load(&context350.nonzero_frames),atomic_load(&context350.invalid_buffers));
    return result;
#undef STEP
}
