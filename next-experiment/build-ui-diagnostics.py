"""Build fresh read-only UI diagnostics, with no OOBE termination or state edits."""
from pathlib import Path
import subprocess

base=Path(__file__).resolve().parent
builder=(base/'build-command-probe.py').read_text()
probe=r'''
#define BOUNDED_SHELL_LIBRARY
#include "bounded-shell.c"
static void ui_read(const char *path) {
    char data[4097];int fd=open(path,O_RDONLY|O_CLOEXEC);
    if(fd<0){printf("LAB875_READ_FAIL path=%s errno=%d\n",path,errno);return;}
    ssize_t n=read(fd,data,sizeof(data)-1);close(fd);
    if(n>0){data[n]=0;printf("LAB875_READ path=%s\n%s\n",path,data);}
}
static void ui_snapshot(void) {
    DIR *d=opendir("/proc");if(!d)return;
    struct dirent *e;
    while((e=readdir(d))) {
        char *end;long pid=strtol(e->d_name,&end,10);if(*end||pid<=1)continue;
        char path[256],name[512]={0};snprintf(path,sizeof(path),"/proc/%ld/cmdline",pid);
        int fd=open(path,O_RDONLY|O_CLOEXEC);if(fd<0)continue;
        ssize_t n=read(fd,name,sizeof(name)-1);close(fd);if(n<=0)continue;
        if(strcmp(name,"com.ohos.sceneboard") && strcmp(name,"com.huawei.hmos.hwstartupguide") && strcmp(name,"foundation") && strcmp(name,"render_service"))continue;
        printf("LAB875_PROCESS pid=%ld name=%s\n",pid,name);
        snprintf(path,sizeof(path),"/proc/%ld/status",pid);ui_read(path);
        snprintf(path,sizeof(path),"/proc/%ld/task",pid);DIR *tasks=opendir(path);if(!tasks)continue;
        struct dirent *t;int count=0;
        while((t=readdir(tasks)) && count<12) {
            char *tail;long tid=strtol(t->d_name,&tail,10);if(*tail||tid<=1)continue;count++;
            const char *files[]={"comm","wchan","stack"};
            for(unsigned i=0;i<sizeof(files)/sizeof(files[0]);i++) {
                snprintf(path,sizeof(path),"/proc/%ld/task/%ld/%s",pid,tid,files[i]);ui_read(path);
            }
        }
        closedir(tasks);
    }
    closedir(d);fflush(stdout);
}
static void command_probe(void) {
    sleep(120);puts("LAB875_READONLY_ENTER");fflush(stdout);
    ui_snapshot();
    lab_shell_run("hilog-recent","/system/bin/hilog -x -z 300",20,"/system/bin/sh");
    lab_shell_run("hilog-ui","/system/bin/hilog -x -e 'SceneBoard|sceneboard|hwstartupguide|AbilityManager|permission|Permission' -z 300",20,"/system/bin/sh");
    lab_shell_run("aa-help","/system/bin/aa help; /system/bin/aa dump -h",10,"/system/bin/sh");
    lab_shell_run("local-logs","ls -l /data/local/tmp; ls -l /data/log/hilog",10,"/system/bin/sh");
    puts("LAB875_DONE desktop_not_assumed=1");fflush(stdout);_exit(0);
}

'''
start=builder.index("probe = r'''")
end=builder.index("source = source.replace(anchor, probe + anchor)")
builder=builder[:start]+"probe = "+repr(probe)+"\n"+builder[end:]
builder=builder.replace('payload-873','payload-875').replace('command-probe-873','command-probe-875')
remote='/home/zoinve/.local/share/harmony-arm64-kvm-lab/command-probe-875'
subprocess.run(['ssh','matebook','mkdir '+remote],check=True)
exec(compile(builder,str(base/'build-command-probe.py'),'exec'),{'__file__':str(base/'build-command-probe.py')})
