"""Extend the proven playback backend with shared-card duplex and real capture."""
from pathlib import Path
import runpy

BASE=Path(__file__).resolve().parent
REPLACE=runpy.run_path(str(BASE/'native-audio-vdi-319.py'))['replace_function']

def server411():
    source=(BASE/'native-audio-server-316.c').read_text()
    source=source.replace('#include <signal.h>','#include <signal.h>\n#include <pthread.h>\n#include <stdatomic.h>')
    source=source.replace('#include "native-audio-protocol-315.h"','#include "native-audio-protocol-412.h"')
    source=source.replace('static volatile sig_atomic_t stopping;',
        '_Static_assert(ATOMIC_INT_LOCK_FREE==2,"signal-safe atomic stop flag");\nstatic _Atomic int stopping;')
    source=source.replace('    long (*snd_pcm_writei)',
        '    long (*snd_pcm_readi)(snd_pcm_t *,void *,unsigned long);\n    long (*snd_pcm_writei)',1)
    source=source.replace('LOAD(snd_pcm_writei);','LOAD(snd_pcm_writei); LOAD(snd_pcm_readi);',1)
    source=source.replace('    uint64_t submitted;','    uint64_t submitted,captured;',1)
    source=REPLACE(source,'device363(','')
    source=REPLACE(source,'pcm363(','')
    source=source.replace('static int jack363(void)','static int jack410(const char *name)')
    source=source.replace('alsa.snd_ctl_elem_value_set_name(value,"Headphone Jack");',
        'alsa.snd_ctl_elem_value_set_name(value,name);')
    source=REPLACE(source,'route363(',r'''
static int route363(struct stream316 *stream,unsigned route)
{
    if(!device410(route))return -ENOTSUP;
    stream->route=route;
    int jack=jack410(route==AUDIO412_HEADSET_MIC?"Mic Jack":"Headphone Jack");
    if(route<2)dprintf(1,"AUDIO363_JACK route=%u state=%d readonly=1\n",route,jack);
    if((route==AUDIO363_HEADPHONES||route==AUDIO412_HEADSET_MIC)&&jack!=1)
        return jack<0?jack:-ENODEV;
    int result=acquire410(route);
    if(result<0)return result;
    stream->device_enabled=1;
    result=alsa.snd_pcm_open(&stream->pcm,pcm410(route),route>=2,1);
    return !result&&!stream->pcm?-EIO:result;
}''')
    source=source.replace('static int route363(', '#include "native-audio-card-410.h"\nstatic int route363(',1)
    source=REPLACE(source,'close316(',r'''
static int close316(struct stream316 *stream)
{
    int result=0;
    if(stream->pcm){
        result=alsa.snd_pcm_drop(stream->pcm);
        int closed=alsa.snd_pcm_close(stream->pcm);
        if(!result&&closed<0)result=closed;
        stream->pcm=NULL;
    }
    if(stream->device_enabled){
        int released=release410(stream->route);
        if(!result&&released<0)result=released;
        stream->device_enabled=0;
    }
    return result;
}''')
    source=REPLACE(source,'open316(',r'''
static int open316(struct stream316 *stream,const struct audio315_config *config)
{
    if(config->magic!=AUDIO315_MAGIC||config->version!=AUDIO315_VERSION||
       config->rate!=48000||config->channels!=2||config->format!=1||!device410(config->route))return -ENOTSUP;
    int result=identity316();if(result)return result;
    result=route363(stream,config->route);if(result<0)return result;
    result=alsa.snd_pcm_set_params(stream->pcm,2,3,2,48000,0,80000);if(result<0)return result;
    result=alsa.snd_pcm_get_params(stream->pcm,&stream->buffer,&stream->period);if(result<0)return result;
    if(!stream->period||stream->period>UINT32_MAX||stream->buffer>UINT32_MAX||
       stream->buffer<stream->period)return -ERANGE;
    if(stream->route<2){
        dprintf(1,"AUDIO316_PCM_READY rate=48000 channels=2 format=S16_LE period=%lu buffer=%lu real_ucm_speaker=%d\n",
            stream->period,stream->buffer,stream->route==AUDIO363_SPEAKER);
        dprintf(1,"AUDIO363_ROUTE_READY route=%u device=%s pcm=%s\n",stream->route,device410(stream->route),pcm410(stream->route));
    }else dprintf(1,"AUDIO411_CAPTURE_READY route=%u device=%s pcm=%s period=%lu buffer=%lu samples_read=0\n",
        stream->route,device410(stream->route),pcm410(stream->route),stream->period,stream->buffer);
    return 0;
}''')
    source=REPLACE(source,'reply316(',r'''
static struct audio315_reply reply316(struct stream316 *stream,int error,unsigned accepted)
{
    struct audio315_reply reply={.magic=AUDIO315_MAGIC,.version=AUDIO315_VERSION,
        .error=error,.accepted_bytes=accepted,.rate=48000,.channels=2,.frame_bytes=4,.route=stream->route};
    if(!stream->pcm)return reply;
    reply.period_frames=(uint32_t)stream->period;reply.buffer_frames=(uint32_t)stream->buffer;
    reply.submitted_frames=stream->submitted;
    long delay=0;
    int result=stream->drained?0:alsa.snd_pcm_delay(stream->pcm,&delay);
    if(result<0||delay<0||(stream->route<2?(uint64_t)delay>stream->submitted:
        (uint64_t)delay>stream->buffer||(uint64_t)delay>UINT64_MAX-stream->submitted)){
        if(!reply.error)reply.error=result<0?result:-EIO;
        return reply;
    }
    reply.delay_frames=delay;
    reply.played_frames=stream->route<2?stream->submitted-(uint64_t)delay:stream->submitted+(uint64_t)delay;
    reply.monotonic_ns=now316();
    if(!reply.monotonic_ns&&!reply.error)reply.error=-EIO;
    return reply;
}''')
    start=source.index('static void client316(')
    end=source.index('static void signal316(',start)
    source=source[:start]+'#include "native-audio-session-411.h"\n'+source[end:]
    start=source.index('int main(int argc,char **argv)')
    source=source[:start]+(BASE/'native-audio-workers-411.h').read_text()
    return source
