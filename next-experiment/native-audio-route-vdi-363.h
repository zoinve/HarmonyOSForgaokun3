#ifndef NATIVE_AUDIO_ROUTE_VDI_363_H
#define NATIVE_AUDIO_ROUTE_VDI_363_H
static void init_render(struct NativeRender *,const struct AudioSampleAttributesVdi *);
static int32_t r_stop(struct IAudioRenderVdi *);
static pthread_mutex_t audio363_adapter_lock=PTHREAD_MUTEX_INITIALIZER;
static struct NativeRender *audio363_render;

static unsigned audio363_pin(enum AudioPortPinVdi pin)
{
    if(pin==PIN_VDI_OUT_SPEAKER)return AUDIO363_SPEAKER;
    if(pin==PIN_VDI_OUT_HEADPHONE||pin==PIN_VDI_OUT_HEADSET)return AUDIO363_HEADPHONES;
    return UINT32_MAX;
}
/* Caller holds render lock. A failed headphone switch stays silent, never falls back. */
static int audio363_switch(struct NativeRender *render,unsigned route)
{
    if(route>AUDIO363_HEADPHONES)return NOT_SUPPORTED;
    if(route==render->route)return audio319_query(render,AUDIO315_POSITION);
    bool started=render->started;render->started=false;
    int result=OK;
    if(render->pcm_fd>=0){
        result=audio319_query(render,AUDIO315_CLOSE);
        if(!result)render->played_base+=render->status.played_frames;
        close(render->pcm_fd);render->pcm_fd=-1;
    }
    render->route=route;render->ever_opened=false;
    memset(&render->status,0,sizeof(render->status));
    if(result)return result;
    result=audio319_open(render);
    render->started=started&&!result;
    return result;
}
static int32_t a_create_render(struct IAudioAdapterVdi *self,const struct AudioDeviceDescriptorVdi *device,
    const struct AudioSampleAttributesVdi *attrs,struct IAudioRenderVdi **out)
{
    (void)self;if(!out)return ERR;*out=NULL;
    if(!device||!audio317_attributes(attrs))return NOT_SUPPORTED;
    unsigned route=audio363_pin(device->pins);
    if(route>AUDIO363_HEADPHONES)return NOT_SUPPORTED;
    pthread_mutex_lock(&audio363_adapter_lock);
    if(audio363_render){pthread_mutex_unlock(&audio363_adapter_lock);return ERR;}
    struct NativeRender *render=calloc(1,sizeof(*render));
    if(!render){pthread_mutex_unlock(&audio363_adapter_lock);return ERR;}
    init_render(render,attrs);render->route=route;audio363_render=render;*out=&render->api;
    pthread_mutex_unlock(&audio363_adapter_lock);return OK;
}
static int32_t a_destroy_render(struct IAudioAdapterVdi *self,struct IAudioRenderVdi *api)
{
    (void)self;if(!api)return ERR;
    pthread_mutex_lock(&audio363_adapter_lock);
    struct NativeRender *render=(struct NativeRender *)api;
    if(render!=audio363_render){pthread_mutex_unlock(&audio363_adapter_lock);return ERR;}
    int result=r_stop(api);audio363_render=NULL;
    pthread_mutex_destroy(&render->lock);free(render);
    pthread_mutex_unlock(&audio363_adapter_lock);return result;
}
static int32_t a_route(struct IAudioAdapterVdi *self,const struct AudioRouteVdi *route,int32_t *handle)
{
    (void)self;if(!handle)return ERR;*handle=-1;
    if(!route||!route->sources||route->sourcesLen!=1||!route->sinks||route->sinksLen!=1)return NOT_SUPPORTED;
    const struct AudioRouteNodeVdi *source=&route->sources[0],*sink=&route->sinks[0];
    if(source->role!=AUDIO_VDI_PORT_SOURCE_ROLE||source->type!=AUDIO_VDI_PORT_MIX_TYPE||
       sink->role!=AUDIO_VDI_PORT_SINK_ROLE||sink->type!=AUDIO_VDI_PORT_DEVICE_TYPE)return NOT_SUPPORTED;
    unsigned selected=audio363_pin(sink->ext.device.type);
    if(selected>AUDIO363_HEADPHONES)return NOT_SUPPORTED;
    pthread_mutex_lock(&audio363_adapter_lock);int result=OK;
    if(audio363_render){
        pthread_mutex_lock(&audio363_render->lock);
        result=audio363_switch(audio363_render,selected);
        pthread_mutex_unlock(&audio363_render->lock);
    }
    /* Without a render this acknowledges topology support, not initialized hardware. */
    if(!result)*handle=1;
    pthread_mutex_unlock(&audio363_adapter_lock);return result;
}
static int32_t a_release_route(struct IAudioAdapterVdi *self,int32_t handle)
{(void)self;return handle==1?OK:ERR;}
static int32_t r_check_scene(struct IAudioRenderVdi *self,const struct AudioSceneDescriptorVdi *scene,bool *supported)
{
    if(!self||!scene||!supported)return ERR;
    *supported=scene->desc.pins==PIN_VDI_NONE||audio363_pin(scene->desc.pins)<=AUDIO363_HEADPHONES;
    return OK;
}
static int32_t r_select_scene(struct IAudioRenderVdi *self,const struct AudioSceneDescriptorVdi *scene)
{
    if(!self||!scene)return ERR;
    struct NativeRender *render=(struct NativeRender *)self;
    pthread_mutex_lock(&render->lock);
    unsigned selected=scene->desc.pins==PIN_VDI_NONE?render->route:audio363_pin(scene->desc.pins);
    int result=audio363_switch(render,selected);
    pthread_mutex_unlock(&render->lock);return result;
}
#endif
