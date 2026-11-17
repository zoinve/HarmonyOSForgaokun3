"""Keep render363 and add real stereo48k capture with truthful failure semantics."""
from pathlib import Path
import re
import runpy

BASE=Path(__file__).resolve().parent
REPLACE=runpy.run_path(str(BASE/'native-audio-vdi-319.py'))['replace_function']
def vendor414():
    source=runpy.run_path(str(BASE/'native-audio-vdi-363.py'))['vendor363']()
    routes=(BASE/'native-audio-route-vdi-363.h').read_text()
    for name in ['a_route','a_release_route']:routes=REPLACE(routes,name+'(','')
    source=source.replace('#include "native-audio-route-vdi-363.h"',routes)
    capture='struct NativeCapture {'
    begin=source.index(capture);end=source.index('\n};',begin)
    source=source[:end]+'''\n    pthread_mutex_t lock;
    struct audio315_reply status;
    uint64_t position_base;
    unsigned route;
    bool position_known;'''+source[end:]
    functions=re.findall(r'^static[^\n(]*\b(c_\w+)\(',source,re.M)
    for name in functions:source=REPLACE(source,name+'(','')
    for name in ['init_capture','a_create_capture','a_destroy_capture','a_set_mic','a_get_mic']:
        source=REPLACE(source,name+'(','')
    source=source.replace('static int32_t a_init(', '#include "native-audio-capture-vdi-413.h"\nstatic int32_t a_init(',1)
    source=REPLACE(source,'a_cap(',r'''
static int32_t a_cap(struct IAudioAdapterVdi *self,const struct AudioPortVdi *port,struct AudioPortCapabilityVdi *cap)
{
    (void)self;if(!port||!cap)return ERR;
    if(!((port->dir==PORT_VDI_OUT&&port->portId==0)||(port->dir==PORT_VDI_IN&&port->portId==1)))return NOT_SUPPORTED;
    memset(cap,0,sizeof(*cap));cap->deviceType=AUDIO_VDI_PRIMARY_DEVICE;cap->deviceId=port->portId;
    cap->sampleRateMasks=AUDIO_VDI_SAMPLE_RATE_MASK_48000;cap->channelMasks=AUDIO_VDI_CHANNEL_STEREO;cap->channelCount=2;
    return OK;
}''')
    source=source.replace('calloc(1,sizeof(*d[0].ports))','calloc(2,sizeof(*d[0].ports))')
    source=source.replace('d[0].portsLen=1;','d[0].portsLen=2;')
    anchor='    d[0].ports[0]=(struct AudioPortVdi){PORT_VDI_OUT,0,strdup("primary_output")};'
    assert source.count(anchor)==1
    source=source.replace(anchor,anchor+'\n    d[0].ports[1]=(struct AudioPortVdi){PORT_VDI_IN,1,strdup("primary_input")};')
    source=source.replace('if(!d[0].ports[0].portName)','if(!d[0].ports[0].portName||!d[0].ports[1].portName)')
    return source
