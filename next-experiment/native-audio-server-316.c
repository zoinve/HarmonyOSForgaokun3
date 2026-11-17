/* Real SC8280XP ALSA playback. No null PCM, simulated clock, or capture fallback. */
#define _GNU_SOURCE
#include <dlfcn.h>
#include <fcntl.h>
#include <poll.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <sys/un.h>
#include <time.h>
#include "native-audio-protocol-315.h"
#include "native-audio-metrics-349.h"

/* Opaque handles and public libasound ABI, matching upstream pcm.h/use-case.h. */
typedef struct _snd_pcm snd_pcm_t;
typedef struct snd_use_case_mgr snd_use_case_mgr_t;
typedef struct _snd_ctl snd_ctl_t;
typedef struct _snd_ctl_elem_value snd_ctl_elem_value_t;
struct alsa316 {
    int (*snd_pcm_open)(snd_pcm_t **,const char *,int,int);
    int (*snd_pcm_close)(snd_pcm_t *);
    int (*snd_pcm_set_params)(snd_pcm_t *,int,int,unsigned,unsigned,int,unsigned);
    int (*snd_pcm_get_params)(snd_pcm_t *,unsigned long *,unsigned long *);
    long (*snd_pcm_writei)(snd_pcm_t *,const void *,unsigned long);
    int (*snd_pcm_wait)(snd_pcm_t *,int);
    int (*snd_pcm_delay)(snd_pcm_t *,long *);
    int (*snd_pcm_prepare)(snd_pcm_t *);
    int (*snd_pcm_drop)(snd_pcm_t *);
    int (*snd_pcm_drain)(snd_pcm_t *);
    int (*snd_use_case_mgr_open)(snd_use_case_mgr_t **,const char *);
    int (*snd_use_case_mgr_close)(snd_use_case_mgr_t *);
    int (*snd_use_case_set)(snd_use_case_mgr_t *,const char *,const char *);
    int (*snd_ctl_open)(snd_ctl_t **,const char *,int);
    int (*snd_ctl_close)(snd_ctl_t *);
    int (*snd_ctl_elem_value_malloc)(snd_ctl_elem_value_t **);
    void (*snd_ctl_elem_value_free)(snd_ctl_elem_value_t *);
    void (*snd_ctl_elem_value_set_interface)(snd_ctl_elem_value_t *,int);
    void (*snd_ctl_elem_value_set_name)(snd_ctl_elem_value_t *,const char *);
    int (*snd_ctl_elem_read)(snd_ctl_t *,snd_ctl_elem_value_t *);
    int (*snd_ctl_elem_value_get_boolean)(const snd_ctl_elem_value_t *,unsigned);
};
static struct alsa316 alsa;
static volatile sig_atomic_t stopping;
struct stream316 {
    snd_pcm_t *pcm;
    snd_use_case_mgr_t *ucm;
    unsigned long period,buffer;
    uint64_t submitted;
    int drained,device_enabled;
    unsigned route;
    struct audio349_metrics metrics;
};

static uint64_t now316(void)
{
    struct timespec time;
    if (clock_gettime(CLOCK_MONOTONIC,&time)) return 0;
    return (uint64_t)time.tv_sec*1000000000ULL+(unsigned long)time.tv_nsec;
}
static int load316(void)
{
    void *library=dlopen("libasound.so.2",RTLD_NOW|RTLD_LOCAL);
    if (!library) {dprintf(1,"AUDIO316_LIBRARY unavailable=1\n");return -ENOSYS;}
#define LOAD(name) do { *(void **)(&alsa.name)=dlsym(library,#name); if (!alsa.name) return -ENOSYS; } while (0)
    LOAD(snd_pcm_open); LOAD(snd_pcm_close); LOAD(snd_pcm_set_params); LOAD(snd_pcm_get_params);
    LOAD(snd_pcm_writei); LOAD(snd_pcm_wait); LOAD(snd_pcm_delay); LOAD(snd_pcm_prepare);
    LOAD(snd_pcm_drop); LOAD(snd_pcm_drain); LOAD(snd_use_case_mgr_open);
    LOAD(snd_use_case_mgr_close); LOAD(snd_use_case_set);
    LOAD(snd_ctl_open);LOAD(snd_ctl_close);LOAD(snd_ctl_elem_value_malloc);
    LOAD(snd_ctl_elem_value_free);LOAD(snd_ctl_elem_value_set_interface);
    LOAD(snd_ctl_elem_value_set_name);LOAD(snd_ctl_elem_read);LOAD(snd_ctl_elem_value_get_boolean);
#undef LOAD
    return 0;
}
static int identity316(void)
{
    int fd=open("/proc/asound/card0/id",O_RDONLY|O_CLOEXEC|O_NOFOLLOW);
    if (fd<0) return -errno;
    char name[64]={0};ssize_t size=read(fd,name,sizeof(name)-1);close(fd);
    return size>0 && !strcmp(name,"SC8280XPHUAWEIG\n") ? 0 : -ENODEV;
}
static const char *device363(unsigned route)
{return route==AUDIO363_SPEAKER?"Speaker":route==AUDIO363_HEADPHONES?"Headphones":NULL;}
static const char *pcm363(unsigned route)
{return route==AUDIO363_SPEAKER?"hw:SC8280XPHUAWEIG,1":route==AUDIO363_HEADPHONES?"hw:SC8280XPHUAWEIG,0":NULL;}
static int jack363(void)
{
    snd_ctl_t *ctl=NULL;snd_ctl_elem_value_t *value=NULL;
    /* SND_CTL_READONLY=4 and SND_CTL_ELEM_IFACE_CARD=0, public ALSA control.h. */
    int result=alsa.snd_ctl_open(&ctl,"hw:SC8280XPHUAWEIG",4);
    if(result<0)return result;
    result=alsa.snd_ctl_elem_value_malloc(&value);
    if(result>=0){
        alsa.snd_ctl_elem_value_set_interface(value,0);
        alsa.snd_ctl_elem_value_set_name(value,"Headphone Jack");
        result=alsa.snd_ctl_elem_read(ctl,value);
        if(result>=0){
            result=alsa.snd_ctl_elem_value_get_boolean(value,0);
            if(result!=0&&result!=1)result=-EIO;
        }
    }
    if(value)alsa.snd_ctl_elem_value_free(value);
    alsa.snd_ctl_close(ctl);return result;
}
static int route363(struct stream316 *stream,unsigned route)
{
    const char *device=device363(route),*pcm=pcm363(route);
    if(!device||!pcm)return -ENOTSUP;
    stream->route=route;
    int jack=jack363();
    dprintf(1,"AUDIO363_JACK route=%u state=%d readonly=1\n",route,jack);
    if(route==AUDIO363_HEADPHONES&&jack!=1)return jack<0?jack:-ENODEV;
    int result=alsa.snd_use_case_mgr_open(&stream->ucm,"hw:SC8280XPHUAWEIG");
    if(result<0)return result;
    result=alsa.snd_use_case_set(stream->ucm,"_verb","HiFi");
    if(result<0)return result;
    result=alsa.snd_use_case_set(stream->ucm,"_enadev",device);
    if(result<0)return result;
    stream->device_enabled=1;
    return alsa.snd_pcm_open(&stream->pcm,pcm,0,1);
}
static void close316(struct stream316 *stream)
{
    if (stream->pcm) {alsa.snd_pcm_drop(stream->pcm);alsa.snd_pcm_close(stream->pcm);}
    if (stream->ucm) {
        if (stream->device_enabled) alsa.snd_use_case_set(stream->ucm,"_disdev",device363(stream->route));
        alsa.snd_use_case_set(stream->ucm,"_verb","Inactive");
        alsa.snd_use_case_mgr_close(stream->ucm);
    }
    memset(stream,0,sizeof(*stream));
}
static int open316(struct stream316 *stream,const struct audio315_config *config)
{
    if (config->magic!=AUDIO315_MAGIC || config->version!=AUDIO315_VERSION ||
        config->rate!=48000 || config->channels!=2 || config->format!=1 || !device363(config->route))
        return -ENOTSUP;
    int result=identity316();if (result) return result;
    /* Public ALSA enum values: playback0, NONBLOCK1, S16_LE2, RW_INTERLEAVED3. */
    result=route363(stream,config->route);
    if (result<0) return result;
    result=alsa.snd_pcm_set_params(stream->pcm,2,3,2,48000,0,80000);
    if (result<0) return result;
    result=alsa.snd_pcm_get_params(stream->pcm,&stream->buffer,&stream->period);
    if (result<0) return result;
    if (!stream->period || stream->period>UINT32_MAX || stream->buffer>UINT32_MAX) return -ERANGE;
    dprintf(1,"AUDIO316_PCM_READY rate=48000 channels=2 format=S16_LE period=%lu buffer=%lu real_ucm_speaker=%d\n",stream->period,stream->buffer,stream->route==AUDIO363_SPEAKER);
    dprintf(1,"AUDIO363_ROUTE_READY route=%u device=%s pcm=%s\n",stream->route,device363(stream->route),pcm363(stream->route));
    return 0;
}
static int write316(struct stream316 *stream,const unsigned char *data,unsigned bytes,unsigned *accepted)
{
    *accepted=0;
    if (stream->drained) {
        int result=alsa.snd_pcm_prepare(stream->pcm);
        if (result<0) return result;
        stream->drained=0;
    }
    uint64_t start=now316();if (!start) return -EIO;
    while (*accepted<bytes && !stopping) {
        uint64_t now=now316();
        if (now<start || now-start>3000000000ULL) return -ETIMEDOUT;
        long frames=alsa.snd_pcm_writei(stream->pcm,data+*accepted,(bytes-*accepted)/4);
        if (frames==-EAGAIN || frames==0) {
            int result=alsa.snd_pcm_wait(stream->pcm,100);
            if (result<0 && result!=-EINTR) return result;
            continue;
        }
        if (frames<0) return (int)frames;
        if ((unsigned long)frames>(bytes-*accepted)/4) return -EIO;
        audio349_accept(&stream->metrics,data+*accepted,(unsigned)frames);
        *accepted+=(unsigned)frames*4;stream->submitted+=(unsigned long)frames;
    }
    return stopping ? -EINTR : 0;
}
static int drain316(struct stream316 *stream)
{
    uint64_t start=now316();if (!start) return -EIO;
    for (;;) {
        int result=alsa.snd_pcm_drain(stream->pcm);
        if (!result) {stream->drained=1;return 0;}
        if (result!=-EAGAIN) return result;
        uint64_t now=now316();
        if (stopping || now<start || now-start>3000000000ULL) return -ETIMEDOUT;
        struct timespec wait={0,10000000};nanosleep(&wait,NULL);
    }
}
static struct audio315_reply reply316(struct stream316 *stream,int error,unsigned accepted)
{
    struct audio315_reply reply={.magic=AUDIO315_MAGIC,.version=AUDIO315_VERSION,
        .error=error,.accepted_bytes=accepted,.rate=48000,.channels=2,.frame_bytes=4,.route=stream->route};
    if (!stream->pcm) return reply;
    reply.period_frames=(uint32_t)stream->period;reply.buffer_frames=(uint32_t)stream->buffer;
    reply.submitted_frames=stream->submitted;
    long delay=0;
    int result=stream->drained ? 0 : alsa.snd_pcm_delay(stream->pcm,&delay);
    if (result<0 || delay<0 || (uint64_t)delay>stream->submitted) {
        if (!reply.error) reply.error=result<0?result:-EIO;
        return reply;
    }
    reply.delay_frames=delay;reply.played_frames=stream->submitted-(uint64_t)delay;
    /* Timestamp is sampled next to the real delay query, not a synthetic playback clock. */
    reply.monotonic_ns=now316();
    if (!reply.monotonic_ns && !reply.error) reply.error=-EIO;
    return reply;
}
/* Idle renderers stay connected; partial requests retain the socket timeout. */
static int request329(int fd,struct audio315_request *request)
{
    while (!stopping) {
        struct pollfd ready={fd,POLLIN,0};
        int result=poll(&ready,1,200);
        if (result<0 && errno==EINTR) continue;
        if (result<0) return -errno;
        if (!result) continue;
        if (ready.revents&POLLIN) {
            errno=0;
            if (!audio315_receive(fd,request,sizeof(*request))) return 0;
            return errno ? -errno : -EPIPE;
        }
        if (ready.revents&(POLLERR|POLLHUP|POLLNVAL)) return -EPIPE;
    }
    return -ECANCELED;
}
static void client316(int fd)
{
    struct stream316 stream={0};struct audio315_config config;
    int result=-EPROTO;
    if (!audio315_receive(fd,&config,sizeof(config))) result=open316(&stream,&config);
    struct audio315_reply reply=reply316(&stream,result,0);
    if(reply.error)++stream.metrics.operation_errors;
    if (audio315_send(fd,&reply,sizeof(reply)) || reply.error) goto finish;
    unsigned logged=0;unsigned char data[AUDIO315_MAX_BYTES];
    while (!stopping) {
        struct audio315_request request;
        int transport=request329(fd,&request);
        if (transport) {
            dprintf(1,"AUDIO329_TRANSPORT result=%d stopping=%d\n",transport,(int)stopping);
            break;
        }
        unsigned accepted=0;result=0;
        if (request.operation==AUDIO315_WRITE) {
            if (!request.bytes || request.bytes>AUDIO315_MAX_BYTES || request.bytes%4) result=-EINVAL;
            else if (audio315_receive(fd,data,request.bytes)) result=-EIO;
            else result=write316(&stream,data,request.bytes,&accepted);
        } else if (request.bytes) result=-EINVAL;
        else if (request.operation==AUDIO315_DRAIN) result=drain316(&stream);
        else if (request.operation==AUDIO315_FLUSH) {
            result=alsa.snd_pcm_drop(stream.pcm);
            if (!result) result=alsa.snd_pcm_prepare(stream.pcm);
            if (!result) {stream.submitted=0;stream.drained=0;}
        } else if (request.operation!=AUDIO315_POSITION && request.operation!=AUDIO315_CLOSE) result=-ENOTSUP;
        reply=reply316(&stream,result,accepted);
        if(reply.error)++stream.metrics.operation_errors;
        if (logged++<64) dprintf(1,"AUDIO316_IO operation=%u result=%d accepted=%u submitted=%llu played=%llu delay=%lld\n",
            request.operation,reply.error,accepted,(unsigned long long)reply.submitted_frames,
            (unsigned long long)reply.played_frames,(long long)reply.delay_frames);
        if (audio315_send(fd,&reply,sizeof(reply)) || reply.error || request.operation==AUDIO315_CLOSE) break;
    }
finish:
    dprintf(1,"AUDIO316_STREAM_END result=%d submitted=%llu audible_verified=0\n",reply.error,(unsigned long long)stream.submitted);
    dprintf(1,"AUDIO349_ACCEPTED frames=%llu nonzero_frames=%llu peak_abs=%u operation_errors=%u microphone_recorded=0 audible_verified=0 route=%u\n",
        (unsigned long long)stream.metrics.accepted_frames,(unsigned long long)stream.metrics.nonzero_frames,
        stream.metrics.peak_abs,stream.metrics.operation_errors,stream.route);
    close316(&stream);
}
static void signal316(int signal_number) {(void)signal_number;stopping=1;}
int main(int argc,char **argv)
{
    if (argc!=2 || getuid()!=0) return 77;
    signal(SIGPIPE,SIG_IGN);signal(SIGTERM,signal316);signal(SIGINT,signal316);
    if (load316()) return 1;
    if (!strcmp(argv[1],"--silence-probe")) {
        struct stream316 stream={0};
        struct audio315_config config={AUDIO315_MAGIC,AUDIO315_VERSION,48000,2,1,0};
        int result=open316(&stream,&config);unsigned accepted=0;
        unsigned char silence[19200]={0};
        if (!result) result=write316(&stream,silence,sizeof(silence),&accepted);
        if (!result) result=drain316(&stream);
        struct audio315_reply reply=reply316(&stream,result,accepted);
        dprintf(1,"AUDIO316_SILENCE_PROBE result=%d accepted=%u played=%llu audible_verified=0\n",reply.error,accepted,(unsigned long long)reply.played_frames);
        close316(&stream);return reply.error?1:0;
    }
    if (strcmp(argv[1],"/native-target/native-audio315.sock")) return 77;
    int fd=socket(AF_UNIX,SOCK_STREAM|SOCK_CLOEXEC,0);if (fd<0) return 1;
    struct sockaddr_un address={.sun_family=AF_UNIX};strcpy(address.sun_path,argv[1]);
    if (bind(fd,(struct sockaddr *)&address,sizeof(address)) || chmod(argv[1],0600) ||
        chown(argv[1],3127,3127) || listen(fd,2)) {close(fd);return 1;}
    dprintf(1,"AUDIO316_LISTEN allowed_uid=3127 microphone_enabled=0\n");
    while (!stopping) {
        struct timeval timeout={.tv_sec=3};
        struct pollfd ready={fd,POLLIN,0};
        int available=poll(&ready,1,200);
        if (available<0 && errno==EINTR) continue;
        if (available<0 || (ready.revents&(POLLERR|POLLHUP|POLLNVAL))) break;
        if (!available) continue;
        int client=accept4(fd,NULL,NULL,SOCK_CLOEXEC);
        if (client<0) {if (errno==EINTR) continue;break;}
        struct ucred peer;socklen_t size=sizeof(peer);
        if (!getsockopt(client,SOL_SOCKET,SO_PEERCRED,&peer,&size) && peer.uid==3127 &&
            !setsockopt(client,SOL_SOCKET,SO_RCVTIMEO,&timeout,sizeof(timeout)) &&
            !setsockopt(client,SOL_SOCKET,SO_SNDTIMEO,&timeout,sizeof(timeout))) client316(client);
        close(client);
    }
    close(fd);return 0;
}
