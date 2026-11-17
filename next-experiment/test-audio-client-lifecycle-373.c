/* Wire fixtures only: no broker credentials, token or hardware is simulated as acceptance. */
#include "vendor.c"
#include <assert.h>
#include <stdio.h>

struct fixture373 {int fd,error;unsigned route,operation;};
static void *reply373(void *opaque)
{
    struct fixture373 *fixture=opaque;struct audio315_request request;
    assert(!audio315_receive(fixture->fd,&request,sizeof(request)));
    assert(request.operation==fixture->operation);
    unsigned char data[4];
    if(request.bytes){assert(request.bytes==sizeof(data));assert(!audio315_receive(fixture->fd,data,sizeof(data)));}
    struct audio315_reply reply={.magic=AUDIO315_MAGIC,.version=AUDIO315_VERSION,
        .error=fixture->error,.accepted_bytes=request.bytes,.route=fixture->route,
        .rate=48000,.channels=2,.frame_bytes=4,.period_frames=1,.buffer_frames=4,
        .submitted_frames=100,.played_frames=80,.delay_frames=20,.monotonic_ns=123456};
    assert(!audio315_send(fixture->fd,&reply,sizeof(reply)));
    close(fixture->fd);return NULL;
}
static void switch373(int error)
{
    struct AudioSampleAttributesVdi attrs={.sampleRate=48000,.channelCount=2,.format=AUDIO_VDI_FORMAT_TYPE_PCM_16_BIT};
    struct NativeRender render;init_render(&render,&attrs);
    int pair[2];assert(!socketpair(AF_UNIX,SOCK_STREAM,0,pair));
    render.pcm_fd=pair[0];render.started=true;render.ever_opened=true;
    struct fixture373 fixture={pair[1],error,AUDIO363_SPEAKER,AUDIO315_CLOSE};
    pthread_t thread;assert(!pthread_create(&thread,NULL,reply373,&fixture));
    pthread_mutex_lock(&render.lock);
    assert(audio363_switch(&render,AUDIO363_HEADPHONES)!=OK);
    pthread_mutex_unlock(&render.lock);
    assert(!pthread_join(thread,NULL));
    assert(render.route==AUDIO363_HEADPHONES&&!render.started&&render.pcm_fd==-1&&!render.ever_opened);
    assert(render.played_base==(error?0:80));
    uint64_t frames;struct AudioTimeStampVdi time;
    assert(r_position(&render.api,&frames,&time)!=OK);
    assert(r_start(&render.api)!=OK&&render.route==AUDIO363_HEADPHONES&&!render.started);
    pthread_mutex_destroy(&render.lock);
}
int main(void)
{
    assert(access(AUDIO315_SOCKET,F_OK)!=0);
    switch373(-EIO);switch373(0);
    struct AudioSampleAttributesVdi attrs={.sampleRate=48000,.channelCount=2,.format=AUDIO_VDI_FORMAT_TYPE_PCM_16_BIT};
    struct NativeRender render;init_render(&render,&attrs);
    int pair[2];assert(!socketpair(AF_UNIX,SOCK_STREAM,0,pair));
    render.pcm_fd=pair[0];render.started=true;render.ever_opened=true;
    struct fixture373 fixture={pair[1],0,AUDIO363_HEADPHONES,AUDIO315_WRITE};
    pthread_t thread;assert(!pthread_create(&thread,NULL,reply373,&fixture));
    int8_t data[4]={0};uint64_t done=123;
    assert(r_frame(&render.api,data,sizeof(data),&done)!=OK&&done==0);
    assert(!render.started&&render.pcm_fd==-1);assert(!pthread_join(thread,NULL));
    pthread_mutex_destroy(&render.lock);
    puts("AUDIO373_LIFECYCLE passed=1 close_failure_stays_on_requested_route=1 failed_headphone_open_stays_silent=1 mismatched_route_bytes_not_acknowledged=1 hardware_acceptance=0");
    return 0;
}
