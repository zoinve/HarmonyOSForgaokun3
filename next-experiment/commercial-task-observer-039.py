"""Bounded passive original-render/application task state; no ptrace or identity changes."""
HELPER=r'''
static void commercial_tasks039(unsigned sample)
{
    if(sample!=15 && sample!=17 && sample!=20 && sample!=24 && sample!=28)return;
    DIR *processes=opendir("/proc");if(!processes)return;
    struct dirent *entry;unsigned matched=0;
    while(matched<4 && (entry=readdir(processes))){
        char *end;long pid=strtol(entry->d_name,&end,10);
        if(!*entry->d_name || *end || pid<=0)continue;
        char path[256],text[4096];
        snprintf(path,sizeof(path),"/proc/%ld/cmdline",pid);
        ssize_t length=read_path(path,text,sizeof(text));if(length<=0)continue;
        if(!strstr(text,"render_service") && !strstr(text,"com.ohos.sceneboard"))continue;
        ++matched;
        struct timespec now={};clock_gettime(CLOCK_MONOTONIC,&now);
        dprintf(commercial_diag_fd003,"COMMERCIAL039_TASK_BEGIN sample=%u pid=%ld mono_sec=%lld command=%s\n",sample,pid,(long long)now.tv_sec,text);
        if(sample==15){
            char maps[32768];snprintf(path,sizeof(path),"/proc/%ld/maps",pid);
            ssize_t count=read_path(path,maps,sizeof(maps));
            if(count>0)dprintf(commercial_diag_fd003,"COMMERCIAL039_MAPS pid=%ld bytes=%zd\n%s\n",pid,count,maps);
        }
        snprintf(path,sizeof(path),"/proc/%ld/task",pid);
        DIR *tasks=opendir(path);if(!tasks)continue;
        struct dirent *task;unsigned count=0;
        while(count<96 && (task=readdir(tasks))){
            char *last;long tid=strtol(task->d_name,&last,10);
            if(!*task->d_name || *last || tid<=0)continue;
            ++count;
            const char *files[]={"comm","stat","wchan","syscall","stack"};
            for(unsigned i=0;i<sizeof(files)/sizeof(files[0]);++i){
                snprintf(path,sizeof(path),"/proc/%ld/task/%ld/%s",pid,tid,files[i]);
                errno=0;ssize_t n=read_path(path,text,sizeof(text));int saved=errno;
                dprintf(commercial_diag_fd003,"COMMERCIAL039_TASK sample=%u pid=%ld tid=%ld file=%s bytes=%zd errno=%d\n",sample,pid,tid,files[i],n,saved);
                if(n>0)dprintf(commercial_diag_fd003,"%s\n",text);
            }
        }
        closedir(tasks);
        dprintf(commercial_diag_fd003,"COMMERCIAL039_TASK_END sample=%u pid=%ld tasks=%u limit=96\n",sample,pid,count);
    }
    closedir(processes);
}
'''
def instrument(source):
    anchor='static void commercial_capture016(unsigned);'
    call='        commercial_capture016(sample);'
    assert source.count(anchor)==source.count(call)==1
    return source.replace(anchor,HELPER+'\n'+anchor,1).replace(call,call+'\n        commercial_tasks039(sample);',1)
