"""Fresh RAM observer: one authorized SIGTERM to the exact OOBE process only."""
from pathlib import Path
import subprocess

base=Path(__file__).resolve().parent
builder=(base/'build-command-probe.py').read_text()
probe=r'''
#define BOUNDED_SHELL_LIBRARY
#include "bounded-shell.c"
#include "oobe-target.h"
static void command_probe(void) {
    sleep(150);
    puts("LAB874_OOBE_OBSERVE_ENTER signal=SIGTERM once=1");fflush(stdout);
    DIR *d=opendir("/proc"); if(!d)_exit(125);
    struct dirent *e; int matched=0;
    while((e=readdir(d))) {
        char *end; long pid=strtol(e->d_name,&end,10);
        if(*end || pid<=1)continue;
        char path[128],name[512]={0};
        snprintf(path,sizeof(path),"/proc/%ld/cmdline",pid);
        int fd=open(path,O_RDONLY|O_CLOEXEC);if(fd<0)continue;
        ssize_t n=read(fd,name,sizeof(name)-1);close(fd);
        if(n<=0 || !memchr(name,0,(size_t)n) || !is_oobe_target(name))continue;
        matched++;
        printf("LAB874_OOBE_EXACT_MATCH pid=%ld name=%s\n",pid,name);fflush(stdout);
        int rc=kill((pid_t)pid,SIGTERM);
        printf("LAB874_OOBE_TERM_RETURN pid=%ld rc=%d errno=%d\n",pid,rc,rc<0?errno:0);fflush(stdout);
    }
    closedir(d);
    printf("LAB874_OOBE_MATCH_COUNT count=%d\n",matched);fflush(stdout);
    sleep(30);
    lab_shell_run("processes-after","ps -A | grep -E 'sceneboard|hwstartupguide|render_service|foundation'",10,"/system/bin/sh");
    lab_shell_run("hilog-help","/system/bin/hilog --help",10,"/system/bin/sh");
    lab_shell_run("hilog-once","/system/bin/hilog -x -t 200",20,"/system/bin/sh");
    puts("LAB874_DONE desktop_not_assumed=1");fflush(stdout);_exit(0);
}

'''
start=builder.index("probe = r'''")
end=builder.index("source = source.replace(anchor, probe + anchor)")
builder=builder[:start]+"probe = "+repr(probe)+"\n"+builder[end:]
builder=builder.replace("payload-873","payload-874").replace("command-probe-873","command-probe-874")
remote='/home/zoinve/.local/share/harmony-arm64-kvm-lab/command-probe-874'
subprocess.run(['ssh','matebook','mkdir '+remote],check=True)
subprocess.run(['scp',str(base/'oobe-target.h'),'matebook:'+remote+'/oobe-target.h'],check=True)
exec(compile(builder,str(base/'build-command-probe.py'),'exec'),{'__file__':str(base/'build-command-probe.py')})
