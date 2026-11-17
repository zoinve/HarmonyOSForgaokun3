#ifndef NATIVE_AUDIO_CAPTURE_CLIENT_413_H
#define NATIVE_AUDIO_CAPTURE_CLIENT_413_H
#include "native-audio-protocol-412.h"

static int audio413_valid(const struct audio315_reply *reply,unsigned route,unsigned limit)
{
    if(route<AUDIO412_MIC||route>AUDIO412_HEADSET_MIC||reply->route!=route||
       reply->magic!=AUDIO315_MAGIC||reply->version!=AUDIO315_VERSION||reply->error>0||
       reply->accepted_bytes>limit||reply->accepted_bytes%4)return 0;
    if(reply->error)return 1;
    return reply->rate==48000&&reply->channels==2&&reply->frame_bytes==4&&reply->period_frames&&
        reply->buffer_frames>=reply->period_frames&&reply->monotonic_ns&&reply->delay_frames>=0&&
        (uint64_t)reply->delay_frames<=reply->buffer_frames&&reply->played_frames>=reply->submitted_frames&&
        reply->played_frames-reply->submitted_frames==(uint64_t)reply->delay_frames;
}
static int audio413_connect(struct audio315_reply *reply,unsigned route)
{
    if(route<AUDIO412_MIC||route>AUDIO412_HEADSET_MIC){errno=EINVAL;return -1;}
    int fd=socket(AF_UNIX,SOCK_STREAM|SOCK_CLOEXEC,0);if(fd<0)return -1;
    struct timeval timeout={.tv_sec=3};
    struct sockaddr_un address={.sun_family=AF_UNIX};strcpy(address.sun_path,AUDIO315_SOCKET);
    if(setsockopt(fd,SOL_SOCKET,SO_RCVTIMEO,&timeout,sizeof(timeout))||
       setsockopt(fd,SOL_SOCKET,SO_SNDTIMEO,&timeout,sizeof(timeout))||
       connect(fd,(struct sockaddr *)&address,sizeof(address)))goto fail;
    struct ucred peer;socklen_t size=sizeof(peer);
    if(getsockopt(fd,SOL_SOCKET,SO_PEERCRED,&peer,&size)||peer.uid!=0){errno=EPERM;goto fail;}
    struct audio315_config config={AUDIO315_MAGIC,AUDIO315_VERSION,48000,2,1,route};
    if(audio315_send(fd,&config,sizeof(config))||audio315_receive(fd,reply,sizeof(*reply)))goto fail;
    if(!audio413_valid(reply,route,0)){errno=EPROTO;goto fail;}
    if(reply->error){errno=-reply->error;goto fail;}
    return fd;
fail:
    {int error=errno;close(fd);errno=error;return -1;}
}
static int audio413_exchange(int fd,unsigned route,unsigned operation,unsigned bytes,
    unsigned char *data,struct audio315_reply *reply)
{
    memset(reply,0,sizeof(*reply));
    if(operation==AUDIO412_READ&&(!data||!bytes||bytes>AUDIO315_MAX_BYTES||bytes%4)){errno=EINVAL;return -1;}
    if(operation!=AUDIO412_READ&&bytes){errno=EINVAL;return -1;}
    struct audio315_request request={operation,bytes};
    if(audio315_send(fd,&request,sizeof(request))||audio315_receive(fd,reply,sizeof(*reply)))return -1;
    if(!audio413_valid(reply,route,bytes)){errno=EPROTO;return -1;}
    if(reply->accepted_bytes&&audio315_receive(fd,data,reply->accepted_bytes))return -1;
    return 0;
}
/* Convert only actual received stereo S16 frames; never pad an unreceived tail. */
static void audio413_convert(unsigned char *out,const unsigned char *in,unsigned frames,
    float gain,enum AudioFormatVdi format)
{
    for(unsigned i=0;i<frames*2;++i){
        int sample=(int16_t)((unsigned)in[i*2]|((unsigned)in[i*2+1]<<8));
        int value=(int)(sample*gain);
        if(format==AUDIO_VDI_FORMAT_TYPE_PCM_16_BIT){
            uint16_t encoded=(uint16_t)value;out[i*2]=(unsigned char)encoded;out[i*2+1]=(unsigned char)(encoded>>8);
        }else{
            uint32_t encoded=(uint32_t)value*65536U;
            for(unsigned b=0;b<4;++b)out[i*4+b]=(unsigned char)(encoded>>(b*8));
        }
    }
}
#endif
