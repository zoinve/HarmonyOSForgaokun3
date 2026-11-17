#ifndef NATIVE_AUDIO_METRICS_349_H
#define NATIVE_AUDIO_METRICS_349_H
/* Aggregate accepted playback only; never retain samples or record a microphone. */
struct audio349_metrics {uint64_t accepted_frames,nonzero_frames;unsigned peak_abs,operation_errors;};
static void audio349_accept(struct audio349_metrics *metrics,const unsigned char *data,unsigned frames)
{
    for(unsigned i=0;i<frames;++i){
        unsigned peak=0;
        for(unsigned channel=0;channel<2;++channel){
            const unsigned char *p=data+i*4+channel*2;
            int value=(int)((unsigned)p[0]|((unsigned)p[1]<<8));
            if(value>=32768)value-=65536;
            unsigned magnitude=(unsigned)(value<0?-value:value);
            if(magnitude>peak)peak=magnitude;
        }
        if(peak)++metrics->nonzero_frames;
        if(peak>metrics->peak_abs)metrics->peak_abs=peak;
    }
    metrics->accepted_frames+=frames;
}
#endif
