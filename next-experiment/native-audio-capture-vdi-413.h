#ifndef NATIVE_AUDIO_CAPTURE_VDI_413_H
#define NATIVE_AUDIO_CAPTURE_VDI_413_H
#include <stdatomic.h>
#include "native-audio-capture-client-413.h"
static struct NativeCapture *capture413;
static _Atomic bool mic413_muted;

static unsigned pin413(enum AudioPortPinVdi pin)
{return pin==PIN_VDI_IN_MIC?AUDIO412_MIC:pin==PIN_VDI_IN_HS_MIC?AUDIO412_HEADSET_MIC:UINT32_MAX;}
static void invalidate413(struct NativeCapture *capture)
{
    if(capture->pcm_fd>=0)close(capture->pcm_fd);
    capture->pcm_fd=-1;capture->started=false;capture->position_known=false;
}
static int open413(struct NativeCapture *capture)
{
    if(capture->mute||mic413_muted)return ERR;
    if(capture->pcm_fd>=0)return OK;
    capture->pcm_fd=audio413_connect(&capture->status,capture->route);
    if(capture->pcm_fd<0){capture->position_known=false;return ERR;}
    capture->position_known=true;return OK;
}
static int query413(struct NativeCapture *capture,unsigned operation)
{
    if(open413(capture))return ERR;
    struct audio315_reply reply;
    if(audio413_exchange(capture->pcm_fd,capture->route,operation,0,NULL,&reply)||reply.error){
        invalidate413(capture);return ERR;
    }
    capture->status=reply;capture->position_known=true;return OK;
}
static int close413(struct NativeCapture *capture)
{
    if(capture->pcm_fd<0)return OK;
    struct audio315_reply reply;
    int result=audio413_exchange(capture->pcm_fd,capture->route,AUDIO315_CLOSE,0,NULL,&reply);
    if(!result&&reply.error)result=ERR;
    if(!result){
        if(reply.played_frames>UINT64_MAX-capture->position_base)result=ERR;
        else{capture->position_base+=reply.played_frames;capture->status=reply;
            capture->status.played_frames=0;capture->position_known=true;}
    }
    if(result)capture->position_known=false;
    close(capture->pcm_fd);capture->pcm_fd=-1;return result?ERR:OK;
}
static int switch413(struct NativeCapture *capture,unsigned route)
{
    if(route<AUDIO412_MIC||route>AUDIO412_HEADSET_MIC)return NOT_SUPPORTED;
    if(route==capture->route)return query413(capture,AUDIO315_POSITION);
    bool running=capture->started;capture->started=false;
    int result=close413(capture);capture->route=route;capture->position_known=false;
    memset(&capture->status,0,sizeof(capture->status));
    if(!result)result=open413(capture);
    capture->started=running&&!result;return result;
}
static int32_t c_frame(struct IAudioCaptureVdi *self,int8_t *frame,uint32_t *length,uint64_t *done)
{
    uint32_t requested=length?*length:0;
    if(length)*length=0;
    if(done)*done=0;
    if(!self||!frame||!length||!done)return ERR;
    struct NativeCapture *capture=(struct NativeCapture *)self;
    pthread_mutex_lock(&capture->lock);int result=ERR;
    unsigned frame_bytes=bytes_per_frame(&capture->attrs);
    if(!requested||requested%frame_bytes||!capture->started||open413(capture))goto finish;
    unsigned char data[AUDIO315_MAX_BYTES];result=OK;
    while(*done<requested){
        unsigned frames=(requested-(unsigned)*done)/frame_bytes;
        if(frames>AUDIO315_MAX_BYTES/4)frames=AUDIO315_MAX_BYTES/4;
        struct audio315_reply reply;
        if(audio413_exchange(capture->pcm_fd,capture->route,AUDIO412_READ,frames*4,data,&reply)){result=ERR;break;}
        unsigned actual=reply.accepted_bytes/4;
        audio413_convert((unsigned char *)frame+*done,data,actual,capture->volume*capture->gain,capture->attrs.format);
        *done+=(uint64_t)actual*frame_bytes;capture->frames+=actual;
        if(reply.error||actual!=frames){result=ERR;capture->position_known=false;break;}
        capture->status=reply;capture->position_known=true;
    }
    *length=(uint32_t)*done;
    if(result)invalidate413(capture);
finish:
    pthread_mutex_unlock(&capture->lock);return result;
}
static int32_t c_frame_ec(struct IAudioCaptureVdi *self,struct AudioCaptureFrameInfoVdi *info)
{
    if(!info)return ERR;
    info->replyBytes=0;info->replyBytesEc=0;
    if(info->frameEcLen)return NOT_SUPPORTED;
    return c_frame(self,info->frame,&info->frameLen,&info->replyBytes);
}
static int32_t c_position(struct IAudioCaptureVdi *self,uint64_t *frames,struct AudioTimeStampVdi *time)
{
    if(!self||!frames||!time)return ERR;
    struct NativeCapture *capture=(struct NativeCapture *)self;
    pthread_mutex_lock(&capture->lock);
    int result=capture->pcm_fd>=0?query413(capture,AUDIO315_POSITION):(capture->position_known?OK:ERR);
    if(!result&&capture->status.played_frames>UINT64_MAX-capture->position_base)result=ERR;
    if(!result){*frames=capture->position_base+capture->status.played_frames;
        time->tvSec=capture->status.monotonic_ns/1000000000ULL;time->tvNSec=capture->status.monotonic_ns%1000000000ULL;}
    pthread_mutex_unlock(&capture->lock);return result;
}
static int32_t c_check_scene(struct IAudioCaptureVdi *self,const struct AudioSceneDescriptorVdi *scene,bool *supported)
{if(!self||!scene||!supported)return ERR;*supported=scene->desc.pins==PIN_VDI_NONE||pin413(scene->desc.pins)!=UINT32_MAX;return OK;}
static int32_t c_scene(struct IAudioCaptureVdi *self,const struct AudioSceneDescriptorVdi *scene)
{
    if(!self||!scene)return ERR;
    struct NativeCapture *capture=(struct NativeCapture *)self;
    pthread_mutex_lock(&capture->lock);
    unsigned route=scene->desc.pins==PIN_VDI_NONE?capture->route:pin413(scene->desc.pins);
    int result=switch413(capture,route);pthread_mutex_unlock(&capture->lock);return result;
}
static int32_t c_set_mute(struct IAudioCaptureVdi *self,bool mute)
{
    if(!self)return ERR;
    struct NativeCapture *capture=(struct NativeCapture *)self;
    pthread_mutex_lock(&capture->lock);capture->mute=mute;
    int result=mute?close413(capture):OK;
    pthread_mutex_unlock(&capture->lock);return result;
}
static int32_t c_get_mute(struct IAudioCaptureVdi *self,bool *mute)
{if(!self||!mute)return ERR;struct NativeCapture *capture=(struct NativeCapture *)self;pthread_mutex_lock(&capture->lock);*mute=capture->mute||mic413_muted;pthread_mutex_unlock(&capture->lock);return OK;}
static int32_t c_set_volume(struct IAudioCaptureVdi *self,float volume)
{if(!self||!isfinite(volume)||volume<0||volume>1)return ERR;struct NativeCapture *capture=(struct NativeCapture *)self;pthread_mutex_lock(&capture->lock);capture->volume=volume;pthread_mutex_unlock(&capture->lock);return OK;}
static int32_t c_get_volume(struct IAudioCaptureVdi *self,float *volume)
{if(!self||!volume)return ERR;struct NativeCapture *capture=(struct NativeCapture *)self;pthread_mutex_lock(&capture->lock);*volume=capture->volume;pthread_mutex_unlock(&capture->lock);return OK;}
static int32_t c_gain_threshold(struct IAudioCaptureVdi *self,float *minimum,float *maximum)
{if(!self||!minimum||!maximum)return ERR;*minimum=0;*maximum=1;return OK;}
static int32_t c_set_gain(struct IAudioCaptureVdi *self,float gain)
{if(!self||!isfinite(gain)||gain<0||gain>1)return ERR;struct NativeCapture *capture=(struct NativeCapture *)self;pthread_mutex_lock(&capture->lock);capture->gain=gain;pthread_mutex_unlock(&capture->lock);return OK;}
static int32_t c_get_gain(struct IAudioCaptureVdi *self,float *gain)
{if(!self||!gain)return ERR;struct NativeCapture *capture=(struct NativeCapture *)self;pthread_mutex_lock(&capture->lock);*gain=capture->gain;pthread_mutex_unlock(&capture->lock);return OK;}
static int32_t c_frame_size(struct IAudioCaptureVdi *self,uint64_t *bytes)
{if(!self||!bytes)return ERR;struct NativeCapture *capture=(struct NativeCapture *)self;pthread_mutex_lock(&capture->lock);*bytes=bytes_per_frame(&capture->attrs);pthread_mutex_unlock(&capture->lock);return OK;}
static int32_t c_frame_count(struct IAudioCaptureVdi *self,uint64_t *frames)
{if(!self||!frames)return ERR;*frames=0;struct NativeCapture *capture=(struct NativeCapture *)self;pthread_mutex_lock(&capture->lock);int result=query413(capture,AUDIO315_POSITION);if(!result)*frames=capture->status.period_frames;pthread_mutex_unlock(&capture->lock);return result;}
static int32_t c_buffer_size(struct IAudioCaptureVdi *self,uint64_t *bytes)
{if(!self||!bytes)return ERR;*bytes=0;struct NativeCapture *capture=(struct NativeCapture *)self;pthread_mutex_lock(&capture->lock);int result=query413(capture,AUDIO315_POSITION);if(!result)*bytes=(uint64_t)capture->status.buffer_frames*bytes_per_frame(&capture->attrs);pthread_mutex_unlock(&capture->lock);return result;}
static int32_t c_set_attrs(struct IAudioCaptureVdi *self,const struct AudioSampleAttributesVdi *attrs)
{
    if(!self||!audio317_attributes(attrs))return NOT_SUPPORTED;
    struct NativeCapture *capture=(struct NativeCapture *)self;
    pthread_mutex_lock(&capture->lock);int result=ERR;
    if(!capture->started&&capture->pcm_fd<0){capture->attrs=*attrs;result=OK;}
    pthread_mutex_unlock(&capture->lock);return result;
}
static int32_t c_get_attrs(struct IAudioCaptureVdi *self,struct AudioSampleAttributesVdi *attrs)
{if(!self||!attrs)return ERR;struct NativeCapture *capture=(struct NativeCapture *)self;pthread_mutex_lock(&capture->lock);*attrs=capture->attrs;pthread_mutex_unlock(&capture->lock);return OK;}
static int32_t c_channel(struct IAudioCaptureVdi *self,uint32_t *channel)
{if(!self||!channel)return ERR;*channel=1;return OK;}
static int32_t c_set_extra(struct IAudioCaptureVdi *self,const char *value)
{(void)self;(void)value;return NOT_SUPPORTED;}
static int32_t c_get_extra(struct IAudioCaptureVdi *self,char *value,uint32_t bytes)
{(void)self;(void)value;(void)bytes;return NOT_SUPPORTED;}
static int32_t c_mmap(struct IAudioCaptureVdi *self,int32_t size,struct AudioMmapBufferDescriptorVdi *desc)
{(void)self;(void)size;(void)desc;return NOT_SUPPORTED;}
static int32_t c_effect(struct IAudioCaptureVdi *self,uint64_t effect)
{(void)self;(void)effect;return NOT_SUPPORTED;}
static int32_t c_start(struct IAudioCaptureVdi *self)
{if(!self)return ERR;struct NativeCapture *capture=(struct NativeCapture *)self;pthread_mutex_lock(&capture->lock);int result=query413(capture,AUDIO315_POSITION);capture->started=!result;pthread_mutex_unlock(&capture->lock);return result;}
static int32_t c_stop(struct IAudioCaptureVdi *self)
{if(!self)return ERR;struct NativeCapture *capture=(struct NativeCapture *)self;pthread_mutex_lock(&capture->lock);capture->started=false;int result=close413(capture);pthread_mutex_unlock(&capture->lock);return result;}
static int32_t c_flush(struct IAudioCaptureVdi *self)
{
    if(!self)return ERR;
    struct NativeCapture *capture=(struct NativeCapture *)self;
    pthread_mutex_lock(&capture->lock);
    int result=capture->pcm_fd>=0?query413(capture,AUDIO315_FLUSH):OK;
    if(!result){capture->frames=0;capture->position_base=0;capture->position_known=false;memset(&capture->status,0,sizeof(capture->status));}
    pthread_mutex_unlock(&capture->lock);return result;
}
static int32_t c_dump(struct IAudioCaptureVdi *self,int32_t range,int32_t fd)
{(void)self;(void)range;(void)fd;return NOT_SUPPORTED;}
static int32_t c_pause_support(struct IAudioCaptureVdi *self,bool *pause,bool *resume)
{if(!self||!pause||!resume)return ERR;*pause=true;*resume=true;return OK;}
static void init_capture(struct NativeCapture *capture,const struct AudioSampleAttributesVdi *attrs)
{
    memset(capture,0,sizeof(*capture));capture->pcm_fd=-1;capture->attrs=*attrs;
    capture->volume=1;capture->gain=1;capture->route=AUDIO412_MIC;pthread_mutex_init(&capture->lock,NULL);
    capture->api=(struct IAudioCaptureVdi){c_frame,c_frame_ec,c_position,c_check_scene,c_scene,c_set_mute,c_get_mute,
        c_set_volume,c_get_volume,c_gain_threshold,c_get_gain,c_set_gain,c_frame_size,c_frame_count,c_set_attrs,
        c_get_attrs,c_channel,c_set_extra,c_get_extra,c_mmap,c_position,c_effect,c_effect,c_buffer_size,c_start,
        c_stop,c_stop,c_start,c_flush,c_stop,c_dump,c_pause_support};
}
static int32_t a_create_capture(struct IAudioAdapterVdi *self,const struct AudioDeviceDescriptorVdi *device,
    const struct AudioSampleAttributesVdi *attrs,struct IAudioCaptureVdi **out)
{
    (void)self;if(!out)return ERR;*out=NULL;
    if(!device||!audio317_attributes(attrs)||pin413(device->pins)==UINT32_MAX)return NOT_SUPPORTED;
    pthread_mutex_lock(&audio363_adapter_lock);int result=ERR;
    if(!capture413){
        struct NativeCapture *capture=calloc(1,sizeof(*capture));
        if(capture){init_capture(capture,attrs);capture->route=pin413(device->pins);capture413=capture;*out=&capture->api;result=OK;}
    }
    pthread_mutex_unlock(&audio363_adapter_lock);return result;
}
static int32_t a_destroy_capture(struct IAudioAdapterVdi *self,struct IAudioCaptureVdi *api)
{
    (void)self;if(!api)return ERR;
    pthread_mutex_lock(&audio363_adapter_lock);int result=ERR;
    if(capture413==(struct NativeCapture *)api){result=c_stop(api);pthread_mutex_destroy(&capture413->lock);free(capture413);capture413=NULL;}
    pthread_mutex_unlock(&audio363_adapter_lock);return result;
}
static int32_t a_set_mic(struct IAudioAdapterVdi *self,bool mute)
{
    if(!self)return ERR;
    pthread_mutex_lock(&audio363_adapter_lock);mic413_muted=mute;
    int result=OK;
    if(mute&&capture413){pthread_mutex_lock(&capture413->lock);result=close413(capture413);pthread_mutex_unlock(&capture413->lock);}
    pthread_mutex_unlock(&audio363_adapter_lock);return result;
}
static int32_t a_get_mic(struct IAudioAdapterVdi *self,bool *mute)
{if(!self||!mute)return ERR;*mute=mic413_muted;return OK;}
static int32_t a_route(struct IAudioAdapterVdi *self,const struct AudioRouteVdi *route,int32_t *handle)
{
    (void)self;if(!handle)return ERR;*handle=-1;
    if(!route||!route->sources||route->sourcesLen!=1||!route->sinks||route->sinksLen!=1)return NOT_SUPPORTED;
    const struct AudioRouteNodeVdi *source=&route->sources[0],*sink=&route->sinks[0];
    if(source->role!=AUDIO_VDI_PORT_SOURCE_ROLE||sink->role!=AUDIO_VDI_PORT_SINK_ROLE)return NOT_SUPPORTED;
    int input=source->type==AUDIO_VDI_PORT_DEVICE_TYPE&&sink->type==AUDIO_VDI_PORT_MIX_TYPE;
    int output=source->type==AUDIO_VDI_PORT_MIX_TYPE&&sink->type==AUDIO_VDI_PORT_DEVICE_TYPE;
    unsigned selected=input?pin413(source->ext.device.type):output?audio363_pin(sink->ext.device.type):UINT32_MAX;
    if(selected==UINT32_MAX)return NOT_SUPPORTED;
    pthread_mutex_lock(&audio363_adapter_lock);int result=OK;
    if(input&&capture413){pthread_mutex_lock(&capture413->lock);result=switch413(capture413,selected);pthread_mutex_unlock(&capture413->lock);}
    if(output&&audio363_render){pthread_mutex_lock(&audio363_render->lock);result=audio363_switch(audio363_render,selected);pthread_mutex_unlock(&audio363_render->lock);}
    /* No active stream acknowledges topology only, not initialized hardware. */
    if(!result)*handle=input?2:1;
    pthread_mutex_unlock(&audio363_adapter_lock);return result;
}
static int32_t a_release_route(struct IAudioAdapterVdi *self,int32_t handle)
{(void)self;return handle==1||handle==2?OK:ERR;}
#endif
