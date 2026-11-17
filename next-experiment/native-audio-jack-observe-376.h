/* Metadata-only inspection of the original audio_server and its real jack fd. */
#include <linux/input.h>
static void audio376_observe(pid_t target)
{
    char path[256],line[1024];struct stat expected;
    snprintf(path,sizeof(path),"/proc/%d/ns/pid",target);
    if(stat(path,&expected))return;
    DIR *processes=opendir("/proc");if(!processes)return;
    struct dirent *entry;
    while((entry=readdir(processes))){
        char *end;long pid=strtol(entry->d_name,&end,10);
        if(*end||pid<=0)continue;
        struct stat owner,ns;
        snprintf(path,sizeof(path),"/proc/%ld",pid);
        if(stat(path,&owner)||owner.st_uid!=1041)continue;
        snprintf(path,sizeof(path),"/proc/%ld/ns/pid",pid);
        if(stat(path,&ns)||ns.st_dev!=expected.st_dev||ns.st_ino!=expected.st_ino)continue;
        snprintf(path,sizeof(path),"/proc/%ld/comm",pid);
        FILE *file=fopen(path,"r");int match=file&&fgets(line,sizeof(line),file)&&!strcmp(line,"audio_server\n");
        if(file)fclose(file);
        if(!match)continue;
        unsigned maps=0,jacks=0,threads=0;
        snprintf(path,sizeof(path),"/proc/%ld/maps",pid);file=fopen(path,"r");
        if(file){
            while(fgets(line,sizeof(line),file))if(strstr(line,"audio-jack376.so"))++maps;
            fclose(file);
        }
        snprintf(path,sizeof(path),"/proc/%ld/fd",pid);DIR *fds=opendir(path);
        if(fds){
            struct dirent *fd;
            while((fd=readdir(fds))){
                if(!fd->d_name[0]||strspn(fd->d_name,"0123456789")!=strlen(fd->d_name))continue;
                ssize_t size=readlinkat(dirfd(fds),fd->d_name,line,sizeof(line)-1);
                if(size<=0||size>=(ssize_t)sizeof(line)-1)continue;
                line[size]=0;
                if(strncmp(line,"/dev/input/event",16))continue;
                int device=openat(dirfd(fds),fd->d_name,O_RDONLY|O_NONBLOCK|O_CLOEXEC);
                char name[256]={0};
                if(device>=0&&ioctl(device,EVIOCGNAME(sizeof(name)),name)>=0&&
                   !strcmp(name,"SC8280XP-HUAWEI-GAOKUN3 Headset Jack")){
                    ++jacks;dprintf(1,"AUDIO376_REAL_JACK_FD pid=%ld fd=%s node=%s events_read=0\n",pid,fd->d_name,line);
                }
                if(device>=0)close(device);
            }
            closedir(fds);
        }
        snprintf(path,sizeof(path),"/proc/%ld/task",pid);DIR *tasks=opendir(path);
        if(tasks){
            struct dirent *task;
            while((task=readdir(tasks))){
                if(!task->d_name[0]||strspn(task->d_name,"0123456789")!=strlen(task->d_name))continue;
                snprintf(path,sizeof(path),"/proc/%ld/task/%.20s/comm",pid,task->d_name);
                file=fopen(path,"r");
                if(file&&fgets(line,sizeof(line),file)&&!strcmp(line,"OS_InputEvent\n"))++threads;
                if(file)fclose(file);
            }
            closedir(tasks);
        }
        dprintf(1,"AUDIO376_POLICY pid=%ld uid=1041 adapter_maps=%u real_jack_fds=%u input_threads=%u hotplug_acceptance=0\n",
            pid,maps,jacks,threads);
        snprintf(path,sizeof(path),"/proc/%ld/root/vendor/lib64/harmony-graphics/audio-jack376.trace",pid);
        file=fopen(path,"r");
        if(file){
            unsigned lines=0;
            while(lines++<32&&fgets(line,sizeof(line),file))dprintf(1,"%s",line);
            fclose(file);
        }
    }
    closedir(processes);
}
