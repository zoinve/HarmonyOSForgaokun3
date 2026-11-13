"""Observe actual service logs and DRM state without changing graphics behavior."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
previous=runpy.run_path(str(base/'build-native-original-graphics-boot-004.py'))
inner,outer=previous['inner'],previous['outer']
extra=r'''
static void graphics_diagnostics_005(unsigned sample)
{
    DIR *d=opendir("/sys/class/drm");struct dirent *e;
    if(d){while((e=readdir(d))){
        if(e->d_name[0]=='.')continue;
        const char *names[]={"status","enabled","modes","dpms"};
        for(unsigned i=0;i<4;++i){char path[512];
            snprintf(path,sizeof(path),"/sys/class/drm/%s/%s",e->d_name,names[i]);
            diagnostic_file_002(sample,path);
        }
    }closedir(d);}
    diagnostic_file_002(sample,"/sys/kernel/debug/dri/0/state");
    diagnostic_file_002(sample,"/sys/kernel/debug/dri/0/clients");
}
static void graphics_process_005(unsigned sample,long pid,const char *cmd)
{
    static int followed[3];
    int index=strstr(cmd,"render_service")?0:strstr(cmd,"composer_host")?1:strstr(cmd,"allocator_host")?2:-1;
    if(index<0)return;
    if(!followed[index]){
        pid_t logger=fork();
        if(logger==0){
            char id[32];snprintf(id,sizeof(id),"%ld",pid);alarm(65);
            dprintf(1,"NATIVE_GRAPHICS005_HILOG_FOLLOW pid=%ld\n",pid);
            char *const args[]={"/system/bin/hilog","-P",id,NULL};
            execv(args[0],args);_exit(127);
        }
        if(logger>0)followed[index]=1;
    }
    if(sample!=3 && sample!=9)return;
    char path[512];snprintf(path,sizeof(path),"/proc/%ld/wchan",pid);diagnostic_file_002(sample,path);
    snprintf(path,sizeof(path),"/proc/%ld/stack",pid);diagnostic_file_002(sample,path);
    snprintf(path,sizeof(path),"/proc/%ld/fd",pid);
    DIR *d=opendir(path);if(!d)return;struct dirent *e;
    while((e=readdir(d))){
        if(e->d_name[0]=='.')continue;
        char link[512],target[1024];snprintf(link,sizeof(link),"/proc/%ld/fd/%s",pid,e->d_name);
        ssize_t n=readlink(link,target,sizeof(target)-1);if(n<0)continue;target[n]=0;
        dprintf(1,"NATIVE_GRAPHICS005_FD sample=%u pid=%ld fd=%s target=%s\n",sample,pid,e->d_name,target);
        if(strstr(target,"/dev/dri/")){
            snprintf(link,sizeof(link),"/proc/%ld/fdinfo/%s",pid,e->d_name);diagnostic_file_002(sample,link);
        }
    }closedir(d);
}
'''
anchor='static void graphics_observer_047(void)'
assert inner.count(anchor)==1
inner=inner.replace(anchor,extra+'\n'+anchor)
inner=inner.replace('        diagnostic_state_002(sample);','        diagnostic_state_002(sample);\n        graphics_diagnostics_005(sample);')
anchor='                dprintf(1, "NATIVE_GRAPHICS001_PROCESS'
assert inner.count(anchor)==1
inner=inner.replace(anchor,'                graphics_process_005(sample,pid,text);\n'+anchor)
outer=outer.replace('native-original-004-%s','native-original-005-%s')
payload=previous['payload'];offset=payload.index('from pathlib import Path\nimport gzip,hashlib')
payload='inner='+repr(inner)+'\nouter='+repr(outer)+'\n'+payload[offset:]
payload=payload.replace('native-original-graphics-boot-004','native-original-graphics-boot-005')
if __name__=='__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
