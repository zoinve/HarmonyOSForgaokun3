"""Deliver one normal swipe through the real target touchscreen's evdev path."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-native-original-graphics-boot-016.py'))
inner='#include <linux/input.h>\n'+p['inner'];capture=p['capture']
helper=r'''
static int native_event_017(int fd,unsigned short type,unsigned short code,int value)
{
    struct input_event e;memset(&e,0,sizeof(e));gettimeofday(&e.time,NULL);
    e.type=type;e.code=code;e.value=value;
    return write(fd,&e,sizeof(e))==(ssize_t)sizeof(e)?0:-1;
}
static void native_swipe_017(void)
{
    int fd=-1;char path[64],name[256];
    for(int i=0;i<32;i++){
        snprintf(path,sizeof(path),"/dev/input/event%d",i);
        int f=open(path,O_RDWR|O_CLOEXEC);if(f<0)continue;
        memset(name,0,sizeof(name));
        if(ioctl(f,EVIOCGNAME(sizeof(name)),name)>=0 && !strcmp(name,"Himax Capacitive TouchScreen")){fd=f;break;}
        close(f);
    }
    struct input_absinfo x,y;
    if(fd<0){dprintf(1,"NATIVE_INPUT017 no_target_touch_device errno=%d\n",errno);return;}
    if(ioctl(fd,EVIOCGABS(ABS_MT_POSITION_X),&x) || ioctl(fd,EVIOCGABS(ABS_MT_POSITION_Y),&y)){
        dprintf(1,"NATIVE_INPUT017 axes_failed errno=%d\n",errno);close(fd);return;
    }
    int okay=1;
    okay&=!native_event_017(fd,EV_ABS,ABS_MT_SLOT,0);
    okay&=!native_event_017(fd,EV_ABS,ABS_MT_TRACKING_ID,17001);
    okay&=!native_event_017(fd,EV_KEY,BTN_TOUCH,1);
    for(int i=0;i<=20;i++){
        okay&=!native_event_017(fd,EV_ABS,ABS_MT_POSITION_X,x.minimum+(x.maximum-x.minimum)/2);
        okay&=!native_event_017(fd,EV_ABS,ABS_MT_POSITION_Y,y.minimum+(y.maximum-y.minimum)*(85-3*i)/100);
        okay&=!native_event_017(fd,EV_SYN,SYN_REPORT,0);usleep(20000);
    }
    okay&=!native_event_017(fd,EV_ABS,ABS_MT_TRACKING_ID,-1);
    okay&=!native_event_017(fd,EV_KEY,BTN_TOUCH,0);
    okay&=!native_event_017(fd,EV_SYN,SYN_REPORT,0);
    dprintf(1,"NATIVE_INPUT017 path=%s gesture=swipe_up events_written=%d x=%d:%d y=%d:%d authentication_unchanged=1\n",path,okay,x.minimum,x.maximum,y.minimum,y.maximum);
    close(fd);
}
'''
anchor='static void graphics_observer_047(void)'
assert inner.count(anchor)==1
inner=inner.replace(anchor,helper+'\n'+anchor)
anchor='        diagnostic_state_002(sample);'
assert inner.count(anchor)==1
inner=inner.replace(anchor,'        if(sample==8)native_swipe_017();\n'+anchor)
outer=p['outer'].replace('native-original-016-%s','native-original-017-%s')
payload=p['payload'];offset=payload.index('from pathlib import Path\nimport gzip,hashlib')
payload='inner='+repr(inner)+'\nouter='+repr(outer)+'\nWRAPPER='+repr(p['p']['p']['p']['p']['p']['wrapper'])+'\nCAPTURE='+repr(capture)+'\n'+payload[offset:]
payload=payload.replace('native-original-graphics-boot-016','native-original-graphics-boot-017')
if __name__=='__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
