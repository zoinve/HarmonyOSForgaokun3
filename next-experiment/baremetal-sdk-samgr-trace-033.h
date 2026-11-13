/* Bounded read-only register/stack inspection of our direct child. No policy changes. */
#include <sys/ptrace.h>
#include <sys/uio.h>
#include <elf.h>
static void samgr_trace_033(pid_t child)
{
    char path[128], data[4096];
    snprintf(path,sizeof(path),"/proc/%ld/maps",(long)child);
    int fd=open(path,O_RDONLY|O_CLOEXEC);
    dprintf(1,"SELINUX033_MAPS_BEGIN fd=%d errno=%d\n",fd,errno);
    if (fd>=0) {
        for (unsigned i=0;i<32;++i) {
            ssize_t n=read(fd,data,sizeof(data));
            if (n<=0) break;
            (void)write(1,data,(size_t)n);
        }
        close(fd);
    }
    dprintf(1,"SELINUX033_MAPS_END\n");
    for (unsigned sample=0;sample<4;++sample) {
        errno=0;
        if (ptrace(PTRACE_ATTACH,child,NULL,NULL)) {
            dprintf(1,"SELINUX033_TRACE sample=%u attach_error=%d\n",sample,errno);return;
        }
        int status=0,stopped=0;
        for (unsigned i=0;i<200;++i) {
            pid_t p=waitpid(child,&status,WNOHANG|WUNTRACED);
            if (p==child) { stopped=WIFSTOPPED(status); break; }
            if (p<0 && errno!=EINTR) break;
            usleep(1000);
        }
        if (!stopped) {
            (void)ptrace(PTRACE_DETACH,child,NULL,NULL);
            dprintf(1,"SELINUX033_TRACE sample=%u stop_not_observed=1 status=%d\n",sample,status);
            return;
        }
        struct { uint64_t x[31],sp,pc,pstate; } regs={0};
        struct iovec iov={&regs,sizeof(regs)};
        errno=0;
        int rc=ptrace(PTRACE_GETREGSET,child,(void *)(uintptr_t)NT_PRSTATUS,&iov);
        dprintf(1,"SELINUX033_TRACE sample=%u rc=%d errno=%d bytes=%zu pc=%llx sp=%llx fp=%llx lr=%llx\n",
                sample,rc,errno,iov.iov_len,(unsigned long long)regs.pc,(unsigned long long)regs.sp,
                (unsigned long long)regs.x[29],(unsigned long long)regs.x[30]);
        if (!rc && iov.iov_len==sizeof(regs)) {
            uint64_t fp=regs.x[29];
            for (unsigned frame=0;frame<12 && !(fp&15) && fp>=regs.sp && fp-regs.sp<1024*1024;++frame) {
                errno=0; long next=ptrace(PTRACE_PEEKDATA,child,(void *)(uintptr_t)fp,NULL);
                if (errno) break;
                errno=0; long lr=ptrace(PTRACE_PEEKDATA,child,(void *)(uintptr_t)(fp+8),NULL);
                if (errno) break;
                dprintf(1,"SELINUX033_FRAME sample=%u frame=%u fp=%llx lr=%llx\n",sample,frame,
                        (unsigned long long)fp,(unsigned long long)(uint64_t)lr);
                if ((uint64_t)next<=fp) break;
                fp=(uint64_t)next;
            }
        }
        errno=0; rc=ptrace(PTRACE_DETACH,child,NULL,NULL);
        dprintf(1,"SELINUX033_DETACH sample=%u rc=%d errno=%d\n",sample,rc,errno);
        if (rc) return;
        usleep(20000);
    }
}
