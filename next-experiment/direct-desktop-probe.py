"""One fresh experiment: normal aa commands, no process killing/state forgery."""
def direct_probe(source, bounded):
    root='static int lab_root_run'+bounded.split('static int lab_shell_run',1)[1].split('#ifndef BOUNDED_SHELL_LIBRARY',1)[0]
    root=root.replace('2000','0').replace('LAB873','LAB916_ROOT')
    root=root.replace('never an inherited root service\'s identity/token','never a borrowed service identity/token')
    diagnostics=r'''
static int guide_count916(void) {
    int count=0;DIR *d=opendir("/proc");if(!d)return -1;struct dirent *e;
    while((e=readdir(d))) {
        if(e->d_name[0]<'0'||e->d_name[0]>'9')continue;
        char p[512],name[512];snprintf(p,sizeof(p),"/proc/%s/cmdline",e->d_name);
        int fd=open(p,O_RDONLY|O_CLOEXEC);if(fd<0)continue;
        ssize_t n=read(fd,name,sizeof(name));close(fd);
        if(n>0&&memchr(name,0,(size_t)n)&&!strcmp(name,"com.huawei.hmos.hwstartupguide")) {
            printf("LAB916_GUIDE pid=%s\n",e->d_name);count++;
        }
    }
    closedir(d);return count;
}
static void direct916(void) {
    printf("LAB916_BEGIN guide_count=%d\n",guide_count916());fflush(stdout);
    lab_shell_run("direct916-shell-identity","id; cat /proc/self/attr/current; grep CapEff /proc/self/status",10,"/system/bin/sh");
    lab_shell_run("direct916-shell-start","/system/bin/aa start -b com.ohos.sceneboard -a com.ohos.sceneboard.MainAbility -m pc_sceneboard",20,"/system/bin/sh");
    lab_shell_run("direct916-shell-stop","/system/bin/aa force-stop com.huawei.hmos.hwstartupguide",20,"/system/bin/sh");
    sleep(15);int count=guide_count916();printf("LAB916_AFTER_SHELL count=%d\n",count);fflush(stdout);
    if(count>0) {
        /* Own root diagnostic child, caps cleared; no foreign token/identity inherited. */
        lab_root_run("direct916-root-identity","id; cat /proc/self/attr/current; grep CapEff /proc/self/status",10,"/system/bin/sh");
        lab_root_run("direct916-root-start","/system/bin/aa start -b com.ohos.sceneboard -a com.ohos.sceneboard.MainAbility -m pc_sceneboard",20,"/system/bin/sh");
        lab_root_run("direct916-root-stop","/system/bin/aa force-stop com.huawei.hmos.hwstartupguide",20,"/system/bin/sh");
    } else puts("LAB916 skip_root_if_guide_absent");
    for(int i=0;i<3;i++){sleep(15);printf("LAB916_VERIFY index=%d guide_count=%d\n",i,guide_count916());fflush(stdout);}
    puts("LAB916_DONE desktop_not_assumed=1");fflush(stdout);
}
'''
    anchor='static void command_probe(void) {'
    assert source.count(anchor)==1
    source=source.replace(anchor,root+diagnostics+anchor)
    anchor='    gpu913_observe();'
    assert source.count(anchor)==1
    return source.replace(anchor,anchor+'\n    direct916();')
