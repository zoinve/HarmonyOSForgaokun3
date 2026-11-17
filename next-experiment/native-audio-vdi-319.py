"""Adapt the supplied VDI to acknowledged real playback, preserving its public ABI."""
from pathlib import Path
import re

BASE=Path(__file__).resolve().parent

def replace_function(source,name,replacement):
    match=re.search(r'^static[^\n]*\b'+re.escape(name),source,re.M)
    assert match,name
    start=match.start()
    opening=source.index('{',start)
    depth=1;end=opening+1
    while depth:
        depth+=(source[end]=='{')-(source[end]=='}');end+=1
    return source[:start]+replacement.strip()+'\n'+source[end:]

def vendor319():
    source=(BASE.parent/'references/L410-HarmonyOS-Adaptations/audio/l410_audio_vdi.c').read_text()
    source=source.replace('#include "l410_audio_alsa_client.h"','#include "native-audio-client-317.h"')
    source=source.replace('    int pcm_fd;\n    enum AudioChannelModeVdi',
        '    int pcm_fd;\n    pthread_mutex_t lock;\n    struct audio315_reply status;\n    uint64_t played_base;\n    bool ever_opened;\n    unsigned route;\n    enum AudioChannelModeVdi',1)
    source=replace_function(source,'mono_ns(', '')
    source=replace_function(source,'pace(', '')
    helper=r'''
static int audio319_open(struct NullRender *r)
{
    if (!audio317_attributes(&r->attrs)) return ERR;
    if (r->pcm_fd>=0) return OK;
    r->pcm_fd=r->route==AUDIO363_SPEAKER?audio317_connect(&r->status):audio363_connect(&r->status,r->route);
    if (r->pcm_fd<0) return ERR;
    r->ever_opened=true;return OK;
}
static int audio319_query(struct NullRender *r,unsigned operation)
{
    if (audio319_open(r)) return ERR;
    struct audio315_reply reply;
    if (audio317_exchange(r->pcm_fd,operation,NULL,0,&reply) || reply.error || reply.route!=r->route) return ERR;
    r->status=reply;return OK;
}
'''
    source=source.replace('static void stamp(',helper+'\nstatic void stamp(',1)
    changes={
    'r_latency(':r'''static int32_t r_latency(struct IAudioRenderVdi *self,uint32_t *ms)
{struct NullRender *r=(struct NullRender *)self;if(!r||!ms)return ERR;pthread_mutex_lock(&r->lock);int result=audio319_query(r,AUDIO315_POSITION);if(!result)*ms=(uint32_t)((r->status.delay_frames*1000+47999)/48000);pthread_mutex_unlock(&r->lock);return result;}''',
    'r_frame(':r'''static int32_t r_frame(struct IAudioRenderVdi *self,const int8_t *frame,uint32_t len,uint64_t *done)
{
    struct NullRender *r=(struct NullRender *)self;
    if(!r||!frame||!done)return ERR;
    *done=0;
    pthread_mutex_lock(&r->lock);
    int result=ERR;
    unsigned input_frame=bytes_per_frame(&r->attrs);
    if(len%input_frame)goto finish;
    if(!r->started||audio319_open(r))goto finish;
    unsigned char buffer[AUDIO315_MAX_BYTES];
    result=OK;
    while(*done<len){
        unsigned frames=(len-(unsigned)*done)/input_frame;
        if(frames>AUDIO315_MAX_BYTES/4)frames=AUDIO315_MAX_BYTES/4;
        unsigned size=frames*4;
        audio317_convert(buffer,(const unsigned char *)frame+*done,frames,r->mute?0:r->volume*r->gain,r->channel_mode,r->attrs.format);
        struct audio315_reply reply;
        if(audio317_exchange(r->pcm_fd,AUDIO315_WRITE,buffer,size,&reply)){result=ERR;break;}
        if(reply.route!=r->route){result=ERR;break;}
        *done+=(uint64_t)reply.accepted_bytes/4*input_frame;
        if(reply.error||reply.accepted_bytes!=size||reply.route!=r->route){result=ERR;break;}
        r->status=reply;
    }
    if(result){close(r->pcm_fd);r->pcm_fd=-1;r->started=false;}
finish:
    pthread_mutex_unlock(&r->lock);return result;
}''',
    'r_position(':r'''static int32_t r_position(struct IAudioRenderVdi *self,uint64_t *frames,struct AudioTimeStampVdi *time)
{
    struct NullRender *r=(struct NullRender *)self;if(!r||!frames||!time)return ERR;
    pthread_mutex_lock(&r->lock);
    int result=r->pcm_fd>=0?audio319_query(r,AUDIO315_POSITION):(r->ever_opened?OK:ERR);
    if(!result){*frames=r->played_base+r->status.played_frames;time->tvSec=r->status.monotonic_ns/1000000000ULL;time->tvNSec=r->status.monotonic_ns%1000000000ULL;}
    pthread_mutex_unlock(&r->lock);return result;
}''',
    'r_start(':r'''static int32_t r_start(struct IAudioRenderVdi *self)
{struct NullRender *r=(struct NullRender *)self;if(!r)return ERR;pthread_mutex_lock(&r->lock);int result=audio319_query(r,AUDIO315_POSITION);if(result&&r->pcm_fd>=0){close(r->pcm_fd);r->pcm_fd=-1;result=audio319_open(r);}r->started=!result;pthread_mutex_unlock(&r->lock);return result;}''',
    'r_stop(':r'''static int32_t r_stop(struct IAudioRenderVdi *self)
{
    struct NullRender *r=(struct NullRender *)self;if(!r)return ERR;pthread_mutex_lock(&r->lock);
    int result=OK;r->started=false;
    if(r->pcm_fd>=0){result=audio319_query(r,AUDIO315_CLOSE);if(!result){r->played_base+=r->status.played_frames;r->status.played_frames=0;}close(r->pcm_fd);r->pcm_fd=-1;}
    pthread_mutex_unlock(&r->lock);return result;
}''',
    'r_pause(':r'''static int32_t r_pause(struct IAudioRenderVdi *self){return r_stop(self);}''',
    'r_flush(':r'''static int32_t r_flush(struct IAudioRenderVdi *self)
{struct NullRender *r=(struct NullRender *)self;if(!r)return ERR;pthread_mutex_lock(&r->lock);int result=r->pcm_fd>=0?audio319_query(r,AUDIO315_FLUSH):OK;if(!result){r->frames=0;r->played_base=0;r->status.played_frames=0;}pthread_mutex_unlock(&r->lock);return result;}''',
    'r_drain(':r'''static int32_t r_drain(struct IAudioRenderVdi *self,enum AudioDrainNotifyTypeVdi *type)
{struct NullRender *r=(struct NullRender *)self;if(!r||!type)return ERR;pthread_mutex_lock(&r->lock);int result=audio319_query(r,AUDIO315_DRAIN);if(!result)*type=AUDIO_VDI_DRAIN_NORMAL_MODE;pthread_mutex_unlock(&r->lock);return result;}''',
    'r_frame_count(':r'''static int32_t r_frame_count(struct IAudioRenderVdi *self,uint64_t *value)
{struct NullRender *r=(struct NullRender *)self;if(!r||!value)return ERR;pthread_mutex_lock(&r->lock);int result=audio319_open(r);if(!result)*value=r->status.period_frames;pthread_mutex_unlock(&r->lock);return result;}''',
    'r_buffer_size(':r'''static int32_t r_buffer_size(struct IAudioRenderVdi *self,uint64_t *value)
{struct NullRender *r=(struct NullRender *)self;if(!r||!value)return ERR;pthread_mutex_lock(&r->lock);int result=audio319_open(r);if(!result)*value=(uint64_t)r->status.buffer_frames*bytes_per_frame(&r->attrs);pthread_mutex_unlock(&r->lock);return result;}''',
    'r_frame_size(':r'''static int32_t r_frame_size(struct IAudioRenderVdi *self,uint64_t *value)
{struct NullRender *r=(struct NullRender *)self;if(!r||!value)return ERR;pthread_mutex_lock(&r->lock);*value=bytes_per_frame(&r->attrs);pthread_mutex_unlock(&r->lock);return OK;}''',
    'r_set_attrs(':r'''static int32_t r_set_attrs(struct IAudioRenderVdi *self,const struct AudioSampleAttributesVdi *attrs)
{struct NullRender *r=(struct NullRender *)self;if(!r||!audio317_attributes(attrs))return NOT_SUPPORTED;pthread_mutex_lock(&r->lock);if(r->started&&r->attrs.format!=attrs->format){pthread_mutex_unlock(&r->lock);return ERR;}r->attrs=*attrs;pthread_mutex_unlock(&r->lock);return OK;}''',
    'r_get_attrs(':r'''static int32_t r_get_attrs(struct IAudioRenderVdi *self,struct AudioSampleAttributesVdi *attrs)
{struct NullRender *r=(struct NullRender *)self;if(!r||!attrs)return ERR;pthread_mutex_lock(&r->lock);*attrs=r->attrs;pthread_mutex_unlock(&r->lock);return OK;}''',
    'r_set_speed(':r'''static int32_t r_set_speed(struct IAudioRenderVdi *self,float value)
{(void)self;return value==1.0f?OK:NOT_SUPPORTED;}''',
    'r_callback(':r'''static int32_t r_callback(struct IAudioRenderVdi *self,RenderCallbackVdi callback,void *cookie)
{(void)self;(void)cookie;return callback?NOT_SUPPORTED:OK;}''',
    'r_effect(':r'''static int32_t r_effect(struct IAudioRenderVdi *self,uint64_t id){(void)self;(void)id;return NOT_SUPPORTED;}''',
    'r_set_buffer(':r'''static int32_t r_set_buffer(struct IAudioRenderVdi *self,uint32_t bytes)
{(void)self;(void)bytes;return NOT_SUPPORTED;}''',
    'c_start(':r'''static int32_t c_start(struct IAudioCaptureVdi *self){(void)self;return NOT_SUPPORTED;}''',
    'c_frame(':r'''static int32_t c_frame(struct IAudioCaptureVdi *self,int8_t *frame,uint32_t *len,uint64_t *done)
{(void)self;(void)frame;if(done)*done=0;if(len)*len=0;return NOT_SUPPORTED;}''',
    'c_position(':r'''static int32_t c_position(struct IAudioCaptureVdi *self,uint64_t *frames,struct AudioTimeStampVdi *time)
{(void)self;(void)frames;(void)time;return NOT_SUPPORTED;}''',
    }
    for name,replacement in changes.items():source=replace_function(source,name,replacement)
    source=replace_function(source,'stamp(', '')
    for field,ctype in [('volume','float'),('gain','float'),('mute','bool'),('mode','enum AudioChannelModeVdi')]:
        member='channel_mode' if field=='mode' else field
        setter={'float':'if(!isfinite(value)||value<0||value>1)return ERR;','bool':'',
                'enum AudioChannelModeVdi':'if(value<AUDIO_VDI_CHANNEL_NORMAL||value>=AUDIO_VDI_CHANNEL_MODE_BUTT)return NOT_SUPPORTED;'}[ctype]
        source=replace_function(source,'r_set_'+field+'(',
            f'static int32_t r_set_{field}(struct IAudioRenderVdi *self,{ctype} value)\n'
            '{struct NullRender *r=(struct NullRender *)self;if(!r)return ERR;'+setter+
            f'pthread_mutex_lock(&r->lock);r->{member}=value;pthread_mutex_unlock(&r->lock);return OK;}}')
        source=replace_function(source,'r_get_'+field+'(',
            f'static int32_t r_get_{field}(struct IAudioRenderVdi *self,{ctype} *value)\n'
            '{struct NullRender *r=(struct NullRender *)self;if(!r||!value)return ERR;'
            f'pthread_mutex_lock(&r->lock);*value=r->{member};pthread_mutex_unlock(&r->lock);return OK;}}')
    source=source.replace('    r->pcm_fd=-1;','    r->pcm_fd=-1;\n    pthread_mutex_init(&r->lock,NULL);',1)
    source=source.replace('if(!a||!out)return ERR;struct NullRender',
                          'if(!audio317_attributes(a)||!out)return NOT_SUPPORTED;struct NullRender',1)
    source=replace_function(source,'a_create_render(',r'''static int32_t a_create_render(struct IAudioAdapterVdi *self,const struct AudioDeviceDescriptorVdi *device,const struct AudioSampleAttributesVdi *attrs,struct IAudioRenderVdi **out)
{
    (void)self;if(!out)return ERR;*out=NULL;
    if(!device||device->pins!=PIN_VDI_OUT_SPEAKER||!audio317_attributes(attrs))return NOT_SUPPORTED;
    struct NullRender *render=calloc(1,sizeof(*render));if(!render)return ERR;
    init_render(render,attrs);*out=&render->api;return OK;
}''')
    source=replace_function(source,'a_route(',r'''static int32_t a_route(struct IAudioAdapterVdi *self,const struct AudioRouteVdi *route,int32_t *handle)
{
    (void)self;if(!handle)return ERR;*handle=-1;
    if(!route||route->sourcesLen!=1||!route->sources||route->sinksLen!=1||!route->sinks)return NOT_SUPPORTED;
    const struct AudioRouteNodeVdi *source=&route->sources[0],*sink=&route->sinks[0];
    if(source->role!=AUDIO_VDI_PORT_SOURCE_ROLE||source->type!=AUDIO_VDI_PORT_MIX_TYPE||
       sink->role!=AUDIO_VDI_PORT_SINK_ROLE||sink->type!=AUDIO_VDI_PORT_DEVICE_TYPE||
       sink->ext.device.type!=PIN_VDI_OUT_SPEAKER)return NOT_SUPPORTED;
    *handle=1;return OK;
}''')
    source=source.replace('if(n->pcm_fd>=0)r_stop(r);free(r);',
                          'if(n->pcm_fd>=0)r_stop(r);pthread_mutex_destroy(&n->lock);free(r);',1)
    source=source.replace('AUDIO_VDI_SAMPLE_RATE_MASK_48000|AUDIO_VDI_SAMPLE_RATE_MASK_44100','AUDIO_VDI_SAMPLE_RATE_MASK_48000')
    source=source.replace('calloc(2,sizeof(*d[0].ports))','calloc(1,sizeof(*d[0].ports))').replace('d[0].portsLen=2;','d[0].portsLen=1;')
    source=source.replace('    d[0].ports[1]=(struct AudioPortVdi){PORT_VDI_IN,1,strdup("primary_input")};\n','')
    source=source.replace('if(!d[0].ports[0].portName||!d[0].ports[1].portName)','if(!d[0].ports[0].portName)')
    assert 'pace(' not in source and 'l410_' not in source
    return source.replace('NullRender','NativeRender').replace('NullCapture','NativeCapture').replace('NullAdapter','NativeAdapter')
