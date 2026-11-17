"""Observe Binder proc state using actual outer TGIDs and namespace membership."""
HELPER = r'''
static void commercial_outer_stream044(const char *path,unsigned limit)
{
    int fd=open(path,O_RDONLY|O_CLOEXEC),error=0,eof=0;unsigned total=0,retries=0;
    dprintf(1,"COMMERCIAL044_OUTER_STREAM_BEGIN path=%s limit=%u\n",path,limit);
    if(fd<0)error=errno;
    else{
        char buffer[4096];
        while(total<limit){
            unsigned wanted=limit-total;if(wanted>sizeof(buffer))wanted=sizeof(buffer);
            ssize_t n=read(fd,buffer,wanted);
            if(n<0){if(errno==EINTR && ++retries<4)continue;error=errno;break;}
            if(!n){eof=1;break;}retries=0;
            if(dprintf(1,"%.*s",(int)n,buffer)<0){error=errno;break;}total+=(unsigned)n;
        }
        close(fd);
    }
    dprintf(1,"\nCOMMERCIAL044_OUTER_STREAM_END path=%s bytes=%u eof=%d errno=%d\n",path,total,eof,error);
}
static void commercial_outer_binder044(pid_t child)
{
    char path[256],expected[128]={},actual[128]={},text[4096];
    snprintf(path,sizeof(path),"/proc/%d/ns/pid",child);
    ssize_t length=readlink(path,expected,sizeof(expected)-1);if(length<=0)return;
    expected[length]=0;
    struct stat st;
    if(stat("/sys/kernel/debug/binder/proc",&st)){
        mkdir("/sys/kernel/debug",0755);errno=0;
        int result=mount("debugfs","/sys/kernel/debug","debugfs",MS_NOSUID|MS_NODEV|MS_NOEXEC,NULL);
        dprintf(1,"COMMERCIAL044_OUTER_DEBUGFS result=%d errno=%d\n",result,errno);
    }
    DIR *dir=opendir("/proc");if(!dir)return;
    struct dirent *entry;unsigned matched=0;
    while(matched<4 && (entry=readdir(dir))){
        char *end;long pid=strtol(entry->d_name,&end,10);
        if(!*entry->d_name || *end || pid<=0)continue;
        snprintf(path,sizeof(path),"/proc/%ld/cmdline",pid);
        if(read_text(path,text,sizeof(text)))continue;
        if(!strstr(text,"render_service") && !strstr(text,"com.ohos.sceneboard"))continue;
        snprintf(path,sizeof(path),"/proc/%ld/ns/pid",pid);
        length=readlink(path,actual,sizeof(actual)-1);if(length<=0)continue;
        actual[length]=0;if(strcmp(expected,actual))continue;
        ++matched;
        struct timespec stamp;clock_gettime(CLOCK_MONOTONIC,&stamp);
        dprintf(1,"COMMERCIAL044_OUTER_PROCESS global_pid=%ld target=%d namespace=%s mono_sec=%lld command=%s\n",pid,child,actual,(long long)stamp.tv_sec,text);
        snprintf(path,sizeof(path),"/proc/%ld/status",pid);commercial_outer_stream044(path,8192);
        snprintf(path,sizeof(path),"/sys/kernel/debug/binder/proc/%ld",pid);commercial_outer_stream044(path,262144);
    }
    closedir(dir);
}
'''


def instrument(text):
    anchor = 'static void native_original(void)'
    assert text.count(anchor) == 1
    text = text.replace(anchor, HELPER + '\n' + anchor, 1)
    anchor = 'if(elapsed033%15==0 || elapsed033==85 || elapsed033==89)snapshot();'
    assert text.count(anchor) == 1
    return text.replace(anchor, 'if(elapsed033%15==0 || elapsed033==85 || elapsed033==89){commercial_outer_binder044(child);snapshot();}', 1)
