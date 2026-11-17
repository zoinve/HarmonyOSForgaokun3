/* Local ALSA doubles only. Never claim a plugged headset from these fixtures. */
#define main audio316_program_main
#include "native-audio-server-316.c"
#undef main
#include <assert.h>
static int jack_state,read_result,ucm_calls,pcm_calls;
static char selected_device[32],selected_pcm[64],disabled_device[32];
static int ctl_open363(snd_ctl_t **out,const char *name,int mode)
{assert(!strcmp(name,"hw:SC8280XPHUAWEIG")&&mode==4);*out=(void *)(uintptr_t)1;return 0;}
static int ctl_close363(snd_ctl_t *ctl){assert(ctl);return 0;}
static int value_alloc363(snd_ctl_elem_value_t **out){*out=(void *)(uintptr_t)2;return 0;}
static void value_free363(snd_ctl_elem_value_t *value){assert(value);}
static void value_iface363(snd_ctl_elem_value_t *value,int iface){assert(value&&iface==0);}
static void value_name363(snd_ctl_elem_value_t *value,const char *name){assert(value&&!strcmp(name,"Headphone Jack"));}
static int value_read363(snd_ctl_t *ctl,snd_ctl_elem_value_t *value){assert(ctl&&value);return read_result;}
static int value_bool363(const snd_ctl_elem_value_t *value,unsigned index){assert(value&&!index);return jack_state;}
static int ucm_open363(snd_use_case_mgr_t **out,const char *name)
{assert(!strcmp(name,"hw:SC8280XPHUAWEIG"));++ucm_calls;*out=(void *)(uintptr_t)3;return 0;}
static int ucm_close363(snd_use_case_mgr_t *ucm){assert(ucm);return 0;}
static int ucm_set363(snd_use_case_mgr_t *ucm,const char *key,const char *value)
{
    assert(ucm);
    if(!strcmp(key,"_enadev"))snprintf(selected_device,sizeof(selected_device),"%s",value);
    else if(!strcmp(key,"_disdev"))snprintf(disabled_device,sizeof(disabled_device),"%s",value);
    else assert(!strcmp(key,"_verb")&&(!strcmp(value,"HiFi")||!strcmp(value,"Inactive")));
    return 0;
}
static int pcm_open363(snd_pcm_t **out,const char *name,int stream,int mode)
{assert(!stream&&mode==1);++pcm_calls;snprintf(selected_pcm,sizeof(selected_pcm),"%s",name);*out=(void *)(uintptr_t)4;return 0;}
static int pcm_close363(snd_pcm_t *pcm){assert(pcm);return 0;}
int main(void)
{
    alsa.snd_ctl_open=ctl_open363;alsa.snd_ctl_close=ctl_close363;
    alsa.snd_ctl_elem_value_malloc=value_alloc363;alsa.snd_ctl_elem_value_free=value_free363;
    alsa.snd_ctl_elem_value_set_interface=value_iface363;alsa.snd_ctl_elem_value_set_name=value_name363;
    alsa.snd_ctl_elem_read=value_read363;alsa.snd_ctl_elem_value_get_boolean=value_bool363;
    alsa.snd_use_case_mgr_open=ucm_open363;alsa.snd_use_case_mgr_close=ucm_close363;alsa.snd_use_case_set=ucm_set363;
    alsa.snd_pcm_open=pcm_open363;alsa.snd_pcm_close=pcm_close363;alsa.snd_pcm_drop=pcm_close363;
    struct stream316 stream={0};
    assert(route363(&stream,AUDIO363_HEADPHONES)==-ENODEV&&!ucm_calls&&!pcm_calls);
    read_result=-ENOENT;
    assert(route363(&stream,AUDIO363_HEADPHONES)==-ENOENT&&!ucm_calls&&!pcm_calls);
    read_result=0;jack_state=1;
    assert(!route363(&stream,AUDIO363_HEADPHONES));
    assert(!strcmp(selected_device,"Headphones")&&!strcmp(selected_pcm,"hw:SC8280XPHUAWEIG,0"));
    close316(&stream);assert(!strcmp(disabled_device,"Headphones"));
    jack_state=0;
    assert(!route363(&stream,AUDIO363_SPEAKER));
    assert(!strcmp(selected_device,"Speaker")&&!strcmp(selected_pcm,"hw:SC8280XPHUAWEIG,1"));
    close316(&stream);assert(!strcmp(disabled_device,"Speaker"));
    assert(route363(&stream,2)==-ENOTSUP);
    struct audio315_config old={AUDIO315_MAGIC,1,48000,2,1,0};
    assert(open316(&stream,&old)==-ENOTSUP);
    struct audio315_config bad={AUDIO315_MAGIC,AUDIO315_VERSION,48000,2,1,2};
    assert(open316(&stream,&bad)==-ENOTSUP);
    puts("AUDIO363_ROUTE_TEST passed=1 unplugged_and_unknown_jack_fail_closed=1 routes_are_distinct=1 hardware_headphone_acceptance=0");
    return 0;
}
