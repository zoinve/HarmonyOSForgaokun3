#ifndef NATIVE_AUDIO_CLIENT_317_H
#define NATIVE_AUDIO_CLIENT_317_H
#include <pthread.h>
#include <math.h>
#include <sys/time.h>
#include <sys/un.h>
#include "native-audio-protocol-315.h"

static int audio317_valid(const struct audio315_reply *reply,unsigned limit)
{
    if (reply->magic!=AUDIO315_MAGIC || reply->version!=AUDIO315_VERSION || reply->error>0 ||
        reply->accepted_bytes>limit || reply->accepted_bytes%4) return 0;
    if (reply->error) return 1;
    return reply->rate==48000 && reply->channels==2 && reply->frame_bytes==4 &&
        reply->route<=AUDIO363_HEADPHONES && reply->period_frames && reply->buffer_frames>=reply->period_frames && reply->monotonic_ns &&
        reply->delay_frames>=0 && (uint64_t)reply->delay_frames<=reply->submitted_frames &&
        reply->played_frames==reply->submitted_frames-(uint64_t)reply->delay_frames;
}
static int audio363_connect(struct audio315_reply *reply,unsigned route)
{
    if(route>AUDIO363_HEADPHONES){errno=EINVAL;return -1;}
    int fd=socket(AF_UNIX,SOCK_STREAM|SOCK_CLOEXEC,0);if (fd<0) return -1;
    struct timeval timeout={.tv_sec=3};
    struct sockaddr_un address={.sun_family=AF_UNIX};strcpy(address.sun_path,AUDIO315_SOCKET);
    if (setsockopt(fd,SOL_SOCKET,SO_RCVTIMEO,&timeout,sizeof(timeout)) ||
        setsockopt(fd,SOL_SOCKET,SO_SNDTIMEO,&timeout,sizeof(timeout)) ||
        connect(fd,(struct sockaddr *)&address,sizeof(address))) goto fail;
    struct ucred peer;socklen_t size=sizeof(peer);
    if (getsockopt(fd,SOL_SOCKET,SO_PEERCRED,&peer,&size) || peer.uid!=0) {errno=EPERM;goto fail;}
    struct audio315_config config={AUDIO315_MAGIC,AUDIO315_VERSION,48000,2,1,route};
    if (audio315_send(fd,&config,sizeof(config)) || audio315_receive(fd,reply,sizeof(*reply))) goto fail;
    if (!audio317_valid(reply,0)) {errno=EPROTO;goto fail;}
    if (reply->error) {errno=-reply->error;goto fail;}
    if(reply->route!=route){errno=EPROTO;goto fail;}
    return fd;
fail:
    {int error=errno;close(fd);errno=error;return -1;}
}
static int audio317_connect(struct audio315_reply *reply)
{return audio363_connect(reply,AUDIO363_SPEAKER);}
static int audio317_exchange(int fd,unsigned operation,const void *data,unsigned bytes,struct audio315_reply *reply)
{
    struct audio315_request request={operation,bytes};
    memset(reply,0,sizeof(*reply));
    if (audio315_send(fd,&request,sizeof(request)) || (bytes && audio315_send(fd,data,bytes)) ||
        audio315_receive(fd,reply,sizeof(*reply))) return -1;
    if (!audio317_valid(reply,bytes)) {errno=EPROTO;return -1;}
    return 0;
}
static int audio317_attributes(const struct AudioSampleAttributesVdi *attrs)
{
    return attrs && attrs->sampleRate==48000 && attrs->channelCount==2 &&
        (attrs->format==AUDIO_VDI_FORMAT_TYPE_PCM_16_BIT || attrs->format==AUDIO_VDI_FORMAT_TYPE_PCM_32_BIT);
}
static void audio317_scale(unsigned char *out,const unsigned char *in,unsigned bytes,float gain,int mode)
{
    for (unsigned i=0;i<bytes;i+=4) {
        int left=(int16_t)((unsigned)in[i]|((unsigned)in[i+1]<<8));
        int right=(int16_t)((unsigned)in[i+2]|((unsigned)in[i+3]<<8));
        switch (mode) {
        case AUDIO_VDI_CHANNEL_BOTH_LEFT:right=left;break;
        case AUDIO_VDI_CHANNEL_BOTH_RIGHT:left=right;break;
        case AUDIO_VDI_CHANNEL_EXCHANGE:{int swap=left;left=right;right=swap;break;}
        case AUDIO_VDI_CHANNEL_MIX:left=right=(left+right)/2;break;
        case AUDIO_VDI_CHANNEL_LEFT_MUTE:left=0;break;
        case AUDIO_VDI_CHANNEL_RIGHT_MUTE:right=0;break;
        case AUDIO_VDI_CHANNEL_BOTH_MUTE:left=right=0;break;
        default:break;
        }
        int16_t l=(int16_t)(left*gain),r=(int16_t)(right*gain);
        out[i]=(unsigned char)l;out[i+1]=(unsigned char)((uint16_t)l>>8);
        out[i+2]=(unsigned char)r;out[i+3]=(unsigned char)((uint16_t)r>>8);
    }
}
static void audio317_convert(unsigned char *out,const unsigned char *in,unsigned frames,
    float gain,int mode,enum AudioFormatVdi format)
{
    if (format==AUDIO_VDI_FORMAT_TYPE_PCM_16_BIT) {
        audio317_scale(out,in,frames*4,gain,mode);return;
    }
    for (unsigned i=0;i<frames;++i) {
        const unsigned char *source=in+i*8;
        unsigned char stereo[]={source[2],source[3],source[6],source[7]};
        audio317_scale(out+i*4,stereo,4,gain,mode);
    }
}
#endif
