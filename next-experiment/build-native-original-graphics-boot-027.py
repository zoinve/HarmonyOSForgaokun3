"""Keep 026 hardware fixes; exercise real keyboard shortcut, not privileged aa."""
from pathlib import Path
import runpy,subprocess,re
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-native-original-graphics-boot-026.py'))
inner=p['inner'];outer=p['outer'].replace('native-original-026-%s','native-original-027-%s')
start=inner.index('        if(sample==9){\n            pid_t launch=fork();')
end=inner.index('\n        }',start)+len('\n        }')
inner=inner[:start]+'        if(sample==9)native_keyboard_027();'+inner[end:]
helper=r'''
static void native_keyboard_027(void)
{
    for(unsigned i=0;i<32;++i){
        char path[128],name[256]={0};snprintf(path,sizeof(path),"/dev/input/event%u",i);
        int fd=open(path,O_RDWR|O_CLOEXEC|O_NOFOLLOW);if(fd<0)continue;
        if(ioctl(fd,EVIOCGNAME(sizeof(name)),name)<0 || strcmp(name,"HID 12d1:10b8 Keyboard")){close(fd);continue;}
        struct input_event events[4];memset(events,0,sizeof(events));
        events[0].type=EV_KEY;events[0].code=KEY_LEFTMETA;events[0].value=1;
        events[1].type=EV_KEY;events[1].code=KEY_I;events[1].value=1;
        events[2].type=EV_SYN;events[2].code=SYN_REPORT;
        ssize_t down=write(fd,events,3*sizeof(events[0]));usleep(80000);
        events[0].code=KEY_I;events[0].value=0;events[1].code=KEY_LEFTMETA;events[1].value=0;
        ssize_t up=write(fd,events,3*sizeof(events[0]));close(fd);
        dprintf(1,"NATIVE_SETTINGS027 keyboard_meta_i path=%s down_bytes=%zd up_bytes=%zd auth_unchanged=1\n",path,down,up);
        return;
    }
    dprintf(1,"NATIVE_SETTINGS027 keyboard_missing shortcut_not_sent=1\n");
}
static void native_input_fds_027(unsigned sample)
{
    DIR *proc=opendir("/proc");if(!proc)return;struct dirent *ent;
    while((ent=readdir(proc))){
        if(ent->d_name[0]<'0'||ent->d_name[0]>'9')continue;
        char path[512],cmd[512]={0};snprintf(path,sizeof(path),"/proc/%s/cmdline",ent->d_name);
        int fd=open(path,O_RDONLY|O_CLOEXEC);if(fd<0)continue;ssize_t n=read(fd,cmd,sizeof(cmd)-1);close(fd);
        if(n<=0 || !strstr(cmd,"multimodalinput"))continue;
        snprintf(path,sizeof(path),"/proc/%s/fd",ent->d_name);DIR *fds=opendir(path);if(!fds)continue;
        struct dirent *f;while((f=readdir(fds))){
            if(f->d_name[0]=='.')continue;
            char target[512];ssize_t len=readlinkat(dirfd(fds),f->d_name,target,sizeof(target)-1);
            if(len<0)continue;
            target[len]=0;
            dprintf(1,"NATIVE_INPUT027_FD sample=%u pid=%s fd=%s target=%s\n",sample,ent->d_name,f->d_name,target);
        }closedir(fds);
    }closedir(proc);
}
'''
anchor='static void graphics_observer_047(void)';assert inner.count(anchor)==1
inner=inner.replace(anchor,helper+'\n'+anchor)
inner=inner.replace('dprintf(1,"NATIVE_INPUT026 inventory sample=%u\\n",sample);','native_input_fds_027(sample);\n            dprintf(1,"NATIVE_INPUT026 inventory sample=%u\\n",sample);')
payload=p['payload'].replace('native-original-graphics-boot-026','native-original-graphics-boot-027')
assert 'inner='+repr(p['inner']) in payload and 'outer='+repr(p['outer']) in payload
payload=payload.replace('inner='+repr(p['inner']),'inner='+repr(inner),1).replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
