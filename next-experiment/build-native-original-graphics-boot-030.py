"""Manual interactive session with capped, fsynced original hilog/fault exports."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-native-original-graphics-boot-029.py'))
inner=p['inner'];outer=p['outer'].replace('native-interactive-029-%s','native-interactive-030-%s').replace('NATIVE_INTERACTIVE029','NATIVE_INTERACTIVE030')
helper=(base/'native-continuous-capture-030.h').read_text()
collect=r'''
#include <sys/resource.h>
static void native_persistent_capture030(void)
{
    struct stat a,b;
    if(fstat(198,&a) || fstat(199,&b) || !S_ISREG(a.st_mode) || !S_ISREG(b.st_mode))
        fail("persistent evidence descriptors");
    pid_t logs=fork();
    if(logs<0)fail("persistent hilog collector fork");
    if(!logs){
        close(199);
        if(fcntl(198,F_SETFD,FD_CLOEXEC))_exit(120);
        dprintf(198,"NATIVE_CAPTURE030 original_hilog=1 filtered=0 cap_bytes=134217728 fsync=1\n");
        unsigned retries=0;
        while(retries<60){
            if(fstat(198,&a) || a.st_size>=128*1024*1024-512)break;
            int fds[2];if(pipe(fds))break;
            if(fcntl(fds[0],F_SETFD,FD_CLOEXEC) || fcntl(fds[1],F_SETFD,FD_CLOEXEC)){
                close(fds[0]);close(fds[1]);break;
            }
            pid_t reader=fork();
            if(!reader){
                close(fds[0]);
                if(dup2(fds[1],1)<0 || dup2(fds[1],2)<0)_exit(121);
                close(fds[1]);
                execl("/system/bin/hilog","hilog",(char*)NULL);_exit(127);
            }
            close(fds[1]);
            if(reader<0){close(fds[0]);break;}
            int rc=capture_stream030(fds[0],198,(size_t)(128*1024*1024-512-a.st_size));
            close(fds[0]);kill(reader,SIGTERM);
            int state=0;while(waitpid(reader,&state,0)<0 && errno==EINTR){}
            dprintf(198,"\nNATIVE_CAPTURE030 reader_end=%d status=%d attempt=%u\n",rc,state,retries);
            fsync(198);
            if(rc!=0)break;
            ++retries;sleep(1);
        }
        dprintf(198,"NATIVE_CAPTURE030_STOP collector_only=1 target_still_running=1\n");
        fsync(198);close(198);_exit(0);
    }
    pid_t faults=fork();
    if(faults<0)fail("persistent fault collector fork");
    if(!faults){
        close(198);
        if(dup2(199,1)<0)_exit(122);
        close(199);
        struct rlimit limit={64*1024*1024,64*1024*1024};
        if(setrlimit(RLIMIT_FSIZE,&limit))_exit(123);
        signal(SIGXFSZ,SIG_DFL);
        dprintf(1,"NATIVE_FAULT030 continuous=1 interval_seconds=10 cap_bytes=67108864 original_files_only=1\n");
        for(unsigned tick=0;;++tick){
            struct stat st;
            if(fstat(1,&st) || st.st_size>48*1024*1024){
                dprintf(1,"NATIVE_FAULT030_STOP capacity_reserve=1 target_still_running=1\n");fsync(1);_exit(0);
            }
            native_fault_capture_018(tick);
            if(fsync(1))_exit(124);
            sleep(10);
        }
    }
    /* Only the two capture processes retain LAB file descriptors. Neither
       original init, its services nor the older passive observers inherit them. */
    close(198);close(199);
    dprintf(1,"NATIVE_CAPTURE030_STARTED hilog_pid=%d fault_pid=%d persistent=1 no_target_timeout=1\n",logs,faults);
}
'''
anchor='static void graphics_observer_047(void)'
assert inner.count(anchor)==1
inner=inner.replace(anchor,helper+'\n'+collect+'\n'+anchor)
anchor='    int trace=open("/data/native-composer-007.trace"'
assert inner.count(anchor)==1
inner=inner.replace(anchor,'    native_persistent_capture030();\n'+anchor)
anchor='        pid_t child=clone(native_child,stack+sizeof(stack),CLONE_NEWPID|CLONE_NEWNS|CLONE_NEWNET|SIGCHLD,NULL);'
assert outer.count(anchor)==1
prepare=r'''
        const char *capture_names030[]={"interactive-hilog030.log","interactive-faults030.log"};
        for(unsigned i=0;i<2;++i){
            int fd=openat(run,capture_names030[i],O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC|O_APPEND,0600);
            if(fd<0 || dup2(fd,198+(int)i)<0 || fcntl(198+(int)i,F_SETFD,0)){
                dprintf(1,"NATIVE_CAPTURE030_REFUSED errno=%d\n",errno);hold();
            }
            if(fd!=198+(int)i)close(fd);
        }
        if(fsync(run)){dprintf(1,"NATIVE_CAPTURE030_DIRECTORY_SYNC_FAILED errno=%d\n",errno);hold();}
'''
outer=outer.replace(anchor,prepare+anchor+'\n        close(198);close(199);')
assert 'reboot(' not in outer
payload=p['payload'].replace('native-original-graphics-boot-029','native-original-graphics-boot-030')
assert 'inner='+repr(p['inner']) in payload and 'outer='+repr(p['outer']) in payload
payload=payload.replace('inner='+repr(p['inner']),'inner='+repr(inner),1).replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
