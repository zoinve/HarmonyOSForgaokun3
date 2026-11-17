/* Include the generated VDI; socket fixtures never access physical audio. */
#include "vendor.c"
#include <assert.h>
#include <stdio.h>

struct fixture417 {
    int fd;
    unsigned operation, bytes, payload;
    struct audio315_reply reply;
};
static struct audio315_reply valid417(unsigned bytes)
{
    return (struct audio315_reply){.magic=AUDIO315_MAGIC,.version=AUDIO315_VERSION,
        .rate=48000,.channels=2,.frame_bytes=4,.period_frames=48,.buffer_frames=480,
        .route=AUDIO412_MIC,.accepted_bytes=bytes,.submitted_frames=bytes/4,
        .played_frames=bytes/4+2,.delay_frames=2,.monotonic_ns=1234567890};
}
static void *serve417(void *argument)
{
    struct fixture417 *fixture=argument;
    struct audio315_request request;
    assert(!audio315_receive(fixture->fd,&request,sizeof(request)));
    assert(request.operation==fixture->operation&&request.bytes==fixture->bytes);
    assert(!audio315_send(fixture->fd,&fixture->reply,sizeof(fixture->reply)));
    unsigned char data[]={0xe8,3,0x18,0xfc,0xd0,7,0x30,0xf8};
    assert(fixture->payload<=sizeof(data));
    if(fixture->payload)assert(!audio315_send(fixture->fd,data,fixture->payload));
    close(fixture->fd);return NULL;
}
static pthread_t begin417(struct NativeCapture *capture,struct fixture417 *fixture)
{
    int pair[2];assert(!socketpair(AF_UNIX,SOCK_STREAM,0,pair));
    capture->pcm_fd=pair[0];fixture->fd=pair[1];
    pthread_t thread;assert(!pthread_create(&thread,NULL,serve417,fixture));return thread;
}
static void joined417(pthread_t thread,struct NativeCapture *capture)
{
    assert(!pthread_join(thread,NULL));
    if(capture->pcm_fd>=0){close(capture->pcm_fd);capture->pcm_fd=-1;}
}
int main(void)
{
    struct audio315_reply reply=valid417(4);
    assert(audio413_valid(&reply,AUDIO412_MIC,8));
    reply.route=AUDIO412_HEADSET_MIC;assert(!audio413_valid(&reply,AUDIO412_MIC,8));
    reply=valid417(4);reply.played_frames++;assert(!audio413_valid(&reply,AUDIO412_MIC,8));
    reply=valid417(4);reply.accepted_bytes=3;assert(!audio413_valid(&reply,AUDIO412_MIC,8));
    reply=valid417(12);assert(!audio413_valid(&reply,AUDIO412_MIC,8));
    reply=valid417(4);reply.error=EIO;assert(!audio413_valid(&reply,AUDIO412_MIC,8));
    reply=valid417(4);reply.error=-EIO;assert(audio413_valid(&reply,AUDIO412_MIC,8));
    reply.route=0;assert(!audio413_valid(&reply,AUDIO412_MIC,8));
    assert(audio413_connect(&reply,0)<0&&errno==EINVAL);

    struct AudioSampleAttributesVdi attrs={.sampleRate=48000,.channelCount=2,
        .format=AUDIO_VDI_FORMAT_TYPE_PCM_16_BIT};
    struct NativeCapture capture;init_capture(&capture,&attrs);capture.started=true;
    unsigned char out[16];memset(out,0xa5,sizeof(out));
    struct fixture417 fixture={.operation=AUDIO412_READ,.bytes=8,.payload=8,.reply=valid417(8)};
    pthread_t thread=begin417(&capture,&fixture);
    uint32_t length=8;uint64_t done=99;
    assert(c_frame(&capture.api,(int8_t *)out,&length,&done)==OK&&done==8&&length==8);
    assert(out[0]==0xe8&&out[1]==3&&out[2]==0x18&&out[3]==0xfc&&out[8]==0xa5);
    assert(capture.frames==2&&capture.position_known);joined417(thread,&capture);

    memset(out,0xa5,sizeof(out));capture.started=true;
    fixture=(struct fixture417){.operation=AUDIO412_READ,.bytes=8,.payload=4,.reply=valid417(4)};
    fixture.reply.error=-EIO;thread=begin417(&capture,&fixture);length=8;
    assert(c_frame(&capture.api,(int8_t *)out,&length,&done)!=OK&&done==4&&length==4);
    assert(out[0]==0xe8&&out[4]==0xa5&&!capture.started&&!capture.position_known);
    joined417(thread,&capture);

    memset(out,0xa5,sizeof(out));capture.started=true;
    fixture=(struct fixture417){.operation=AUDIO412_READ,.bytes=8,.payload=4,.reply=valid417(8)};
    thread=begin417(&capture,&fixture);length=8;
    assert(c_frame(&capture.api,(int8_t *)out,&length,&done)!=OK&&!done&&!length);
    for(unsigned i=0;i<sizeof(out);++i)assert(out[i]==0xa5);
    joined417(thread,&capture);

    memset(out,0xa5,sizeof(out));capture.started=true;
    fixture=(struct fixture417){.operation=AUDIO412_READ,.bytes=8,.reply=valid417(0)};
    fixture.reply.route=AUDIO412_HEADSET_MIC;thread=begin417(&capture,&fixture);length=8;
    assert(c_frame(&capture.api,(int8_t *)out,&length,&done)!=OK&&!done&&!length);
    assert(out[0]==0xa5);joined417(thread,&capture);

    unsigned char input[]={0xe8,3,0x18,0xfc};memset(out,0xa5,sizeof(out));
    audio413_convert(out,input,1,0.5f,AUDIO_VDI_FORMAT_TYPE_PCM_16_BIT);
    assert(out[0]==0xf4&&out[1]==1&&out[2]==0x0c&&out[3]==0xfe&&out[4]==0xa5);
    audio413_convert(out,input,1,1,AUDIO_VDI_FORMAT_TYPE_PCM_32_BIT);
    assert(out[0]==0&&out[1]==0&&out[2]==0xe8&&out[3]==3);
    assert(out[4]==0&&out[5]==0&&out[6]==0x18&&out[7]==0xfc&&out[8]==0xa5);

    fixture=(struct fixture417){.operation=AUDIO315_CLOSE,.reply=valid417(0)};
    thread=begin417(&capture,&fixture);capture.started=true;
    assert(c_set_mute(&capture.api,true)==OK&&capture.pcm_fd<0);
    joined417(thread,&capture);length=8;memset(out,0xa5,sizeof(out));
    assert(c_frame(&capture.api,(int8_t *)out,&length,&done)!=OK&&!done&&!length&&out[0]==0xa5);
    assert(c_set_mute(&capture.api,false)==OK);

    fixture=(struct fixture417){.operation=AUDIO315_POSITION,.reply=valid417(0)};
    fixture.reply.error=-EIO;thread=begin417(&capture,&fixture);capture.position_known=true;
    assert(c_start(&capture.api)!=OK&&capture.pcm_fd<0&&!capture.started&&!capture.position_known);
    joined417(thread,&capture);
    fixture=(struct fixture417){.operation=AUDIO315_POSITION,.reply=valid417(0)};
    thread=begin417(&capture,&fixture);
    assert(c_start(&capture.api)==OK&&capture.started&&capture.position_known);
    joined417(thread,&capture);

    struct IAudioCaptureVdi *created=NULL,*other=(void *)(uintptr_t)1;
    struct AudioDeviceDescriptorVdi device={.pins=PIN_VDI_IN_MIC};
    assert(a_create_capture(NULL,&device,&attrs,&created)==OK&&created);
    assert(a_create_capture(NULL,&device,&attrs,&other)!=OK&&!other);
    assert(a_destroy_capture(NULL,created)==OK);
    device.pins=PIN_VDI_OUT_SPEAKER;
    assert(a_create_capture(NULL,&device,&attrs,&created)==NOT_SUPPORTED&&!created);
    pthread_mutex_destroy(&capture.lock);
    puts("AUDIO417 capture_protocol_partial_disconnect_conversion_mute=pass physical_capture=0");
    return 0;
}
