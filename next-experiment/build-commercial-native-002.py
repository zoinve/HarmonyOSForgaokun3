"""Keep commercial payload unchanged; repair a volatile log path and retain early diagnostics."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-commercial-native-001.py'))
extra=r'''
static void commercial_command002(char *const args[])
{
    pid_t p=fork();if(p<0)return;
    if(!p){dup2(199,1);dup2(199,2);execv(args[0],args);_exit(127);}
    int status=0;
    for(unsigned n=0;n<30;++n){
        if(waitpid(p,&status,WNOHANG)==p){
            dprintf(199,"COMMERCIAL002_COMMAND path=%s argument=%s status=%d\n",args[0],args[1],status);return;
        }
        usleep(100000);
    }
    kill(p,SIGKILL);waitpid(p,&status,0);
    dprintf(199,"COMMERCIAL002_COMMAND_TIMEOUT path=%s\n",args[0]);
}
static void commercial_early_kernel002(void)
{
    int fd=open("/dev/kmsg",O_RDONLY|O_NONBLOCK|O_CLOEXEC);
    if(fd<0){dprintf(199,"COMMERCIAL002_KMSG_OPEN errno=%d\n",errno);return;}
    if(lseek(fd,0,SEEK_END)<0){close(fd);return;}
    pid_t p=fork();if(p<0){close(fd);return;}
    if(!p){
        char text[8192];size_t total=0;
        for(unsigned tick=0;tick<600 && total<4*1024*1024;++tick){
            for(unsigned burst=0;burst<64;++burst){
                ssize_t n=read(fd,text,sizeof(text)-1);
                if(n<0){if(errno==EPIPE)continue;break;}
                if(!n)break;
                text[n]=0;dprintf(199,"COMMERCIAL002_KMSG %s",text);total+=(size_t)n;
                if(total>=4*1024*1024)break;
            }
            usleep(100000);
        }
        close(fd);_exit(0);
    }
    close(fd);
}
static void commercial_log_directory002(void)
{
    directory("/data/local",0751);
    directory("/data/local/tmp",0771);
    directory("/data/local/tmp/l410-vulkan-r18",0750);
    if(chown("/data/local/tmp/l410-vulkan-r18",1003,1000) ||
       chmod("/data/local/tmp/l410-vulkan-r18",0750))fail("commercial original render log directory");
}
'''
inner=p['inner'].replace('static void commercial_observer(void)',extra+'\nstatic void commercial_observer(void)',1)
anchor='        sleep(5);\n'
assert inner.count(anchor)==1
inner=inner.replace(anchor,r'''
        if(sample==1 || sample==3 || sample==8){
            char *hdf[]={"/system/bin/param","get","init.svc.hdf_devmgr",NULL};
            char *rs[]={"/system/bin/param","get","init.svc.render_service",NULL};
            commercial_command002(hdf);commercial_command002(rs);
        }
        ssize_t logn=read_path("/data/local/tmp/l410-vulkan-r18/render_service.boot.log",text,sizeof(text));
        if(logn>0)dprintf(199,"COMMERCIAL002_RS_LOG sample=%u bytes=%zd\n%s\n",sample,logn,text);
        sleep(5);
''',1)
anchor='    native_persistent_capture030();'
assert inner.count(anchor)==1
inner=inner.replace(anchor,anchor+r'''
    commercial_log_directory002();
    commercial_early_kernel002();
    char *loader[]={"/lib/ld-musl-aarch64.so.1","--list","/vendor/bin/hdf_devmgr",NULL};
    commercial_command002(loader);
''',1)
outer=p['outer'].replace('commercial61-native-001-%s','commercial61-native-002-%s').replace('COMMERCIAL001','COMMERCIAL002')
payload=p['payload']
assert payload.count('inner='+repr(p['inner']))==1 and payload.count('outer='+repr(p['outer']))==1
payload=payload.replace('inner='+repr(p['inner']),'inner='+repr(inner),1).replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
payload=payload.replace('commercial61-native-001','commercial61-native-002')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
