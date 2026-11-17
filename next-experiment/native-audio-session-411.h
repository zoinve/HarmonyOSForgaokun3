#ifndef NATIVE_AUDIO_SESSION_411_H
#define NATIVE_AUDIO_SESSION_411_H
static int read411(struct stream316 *stream,unsigned char *data,unsigned bytes,unsigned *accepted)
{
    *accepted=0;
    uint64_t start=now316();if(!start)return -EIO;
    while(*accepted<bytes&&!stopping){
        uint64_t now=now316();if(now<start||now-start>3000000000ULL)return -ETIMEDOUT;
        long frames=alsa.snd_pcm_readi(stream->pcm,data+*accepted,(bytes-*accepted)/4);
        if(frames==-EAGAIN||frames==0){
            int result=alsa.snd_pcm_wait(stream->pcm,100);
            if(result<0&&result!=-EINTR)return result;
            continue;
        }
        if(frames<0)return (int)frames;
        if((unsigned long)frames>(bytes-*accepted)/4)return -EIO;
        if((uint64_t)frames>UINT64_MAX-stream->submitted||
           (uint64_t)frames>UINT64_MAX-stream->captured)return -EOVERFLOW;
        *accepted+=(unsigned)frames*4;stream->submitted+=(unsigned long)frames;stream->captured+=(unsigned long)frames;
    }
    return stopping?-EINTR:0;
}
static void client316(int fd)
{
    struct stream316 stream={0};struct audio315_config config;
    int result=-EPROTO;
    if(!audio315_receive(fd,&config,sizeof(config)))result=open316(&stream,&config);
    struct audio315_reply reply=reply316(&stream,result,0);
    if(reply.error)++stream.metrics.operation_errors;
    if(audio315_send(fd,&reply,sizeof(reply))||reply.error)goto finish;
    unsigned logged=0;unsigned char data[AUDIO315_MAX_BYTES];
    while(!stopping){
        struct audio315_request request;
        int transport=request329(fd,&request);
        if(transport){dprintf(1,"AUDIO329_TRANSPORT result=%d stopping=%d\n",transport,(int)stopping);break;}
        unsigned accepted=0;result=0;
        int capture=stream.route>=2;
        if(request.operation==AUDIO315_WRITE||request.operation==AUDIO412_READ){
            if(!request.bytes||request.bytes>AUDIO315_MAX_BYTES||request.bytes%4)result=-EINVAL;
            else if((request.operation==AUDIO412_READ)!=capture)result=-ENOTSUP;
            else if(capture)result=read411(&stream,data,request.bytes,&accepted);
            else if(audio315_receive(fd,data,request.bytes))result=-EIO;
            else result=write316(&stream,data,request.bytes,&accepted);
        }else if(request.bytes)result=-EINVAL;
        else if(request.operation==AUDIO315_DRAIN)result=capture?-ENOTSUP:drain316(&stream);
        else if(request.operation==AUDIO315_FLUSH){
            result=alsa.snd_pcm_drop(stream.pcm);
            if(!result)result=alsa.snd_pcm_prepare(stream.pcm);
            if(!result){stream.submitted=0;stream.drained=0;}
        }else if(request.operation!=AUDIO315_POSITION&&request.operation!=AUDIO315_CLOSE)result=-ENOTSUP;
        reply=reply316(&stream,result,accepted);
        if(request.operation==AUDIO315_CLOSE){
            int closed=close316(&stream);
            if(!reply.error&&closed<0)reply.error=closed;
        }
        if(reply.error)++stream.metrics.operation_errors;
        if(logged++<64){
            if(capture)dprintf(1,"AUDIO411_CAPTURE_IO operation=%u result=%d actual_bytes=%u delivered_frames=%llu sample_bytes_logged=0\n",
                request.operation,reply.error,accepted,(unsigned long long)stream.submitted);
            else dprintf(1,"AUDIO316_IO operation=%u result=%d accepted=%u submitted=%llu played=%llu delay=%lld\n",
                request.operation,reply.error,accepted,(unsigned long long)reply.submitted_frames,
                (unsigned long long)reply.played_frames,(long long)reply.delay_frames);
        }
        if(audio315_send(fd,&reply,sizeof(reply)))break;
        if(capture&&request.operation==AUDIO412_READ&&accepted&&audio315_send(fd,data,accepted))break;
        if(reply.error||request.operation==AUDIO315_CLOSE)break;
    }
finish:
    result=close316(&stream);
    if(result<0)++stream.metrics.operation_errors;
    if(stream.route>=2)dprintf(1,"AUDIO411_CAPTURE_END route=%u actual_frames=%llu cleanup=%d errors=%u sample_bytes_logged=0\n",
        stream.route,(unsigned long long)stream.captured,result,stream.metrics.operation_errors);
    else{
        dprintf(1,"AUDIO316_STREAM_END result=%d submitted=%llu audible_verified=0\n",reply.error,(unsigned long long)stream.submitted);
        dprintf(1,"AUDIO349_ACCEPTED frames=%llu nonzero_frames=%llu peak_abs=%u operation_errors=%u microphone_recorded=0 audible_verified=0 route=%u\n",
            (unsigned long long)stream.metrics.accepted_frames,(unsigned long long)stream.metrics.nonzero_frames,
            stream.metrics.peak_abs,stream.metrics.operation_errors,stream.route);
    }
}
#endif
