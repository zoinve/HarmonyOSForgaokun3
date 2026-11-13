"""Real Unix FD transfer tests; these CPU fixtures are not DMA-BUF/GPU evidence."""
from pathlib import Path
import subprocess

base=Path(__file__).resolve().parent
header=base/'baremetal-buffer-ipc-001.h'
assert header.exists(), 'missing strict buffer/fence FD transport'
source=header.read_text()+r'''
#include <assert.h>
#include <stdio.h>
#include <dirent.h>
#include <sys/wait.h>
#include <signal.h>
static int descriptors(void) {
    DIR *d=opendir("/proc/self/fd"); assert(d); int n=0;
    while(readdir(d))++n;
    closedir(d);return n;
}
static void raw_send(int sock, struct buffer_packet001 *p, int *fds, int count, int extra) {
    char data[sizeof(*p)+1];memcpy(data,p,sizeof(*p));data[sizeof(*p)]=0;
    struct iovec io={data,sizeof(*p)+(size_t)extra};
    union {struct cmsghdr align;char bytes[CMSG_SPACE(12*sizeof(int))];} control={0};
    struct msghdr m={0};m.msg_iov=&io;m.msg_iovlen=1;
    m.msg_control=control.bytes;m.msg_controllen=CMSG_SPACE(count*sizeof(int));
    struct cmsghdr *c=CMSG_FIRSTHDR(&m);c->cmsg_level=SOL_SOCKET;c->cmsg_type=SCM_RIGHTS;
    c->cmsg_len=CMSG_LEN(count*sizeof(int));memcpy(CMSG_DATA(c),fds,count*sizeof(int));
    assert(sendmsg(sock,&m,MSG_NOSIGNAL)==(ssize_t)io.iov_len);
}
int main(void) {
    alarm(5);
    struct buffer_packet001 p={.magic=0x42464631,.width=16,.height=16,
        .stride=256,.format=0x34325241,.offset=0,.modifier=0};
    int s[2];assert(socketpair(AF_UNIX,SOCK_SEQPACKET|SOCK_CLOEXEC,0,s)==0);
    int original[3]={open("/dev/null",O_RDONLY|O_CLOEXEC),open("/dev/zero",O_RDONLY|O_CLOEXEC),-1};
    original[2]=dup(original[0]);assert(original[0]>=0 && original[1]>=0 && original[2]>=0);
    pid_t child=fork();assert(child>=0);
    if(!child) {
        close(s[0]);for(int i=0;i<3;++i)close(original[i]);
        int fds[2];struct buffer_packet001 received={0};
        assert(buffer_recv001(s[1],&received,fds)==0);
        assert(received.stride==256 && fds[0]!=fds[1]);
        assert((fcntl(fds[0],F_GETFD)&FD_CLOEXEC) && (fcntl(fds[1],F_GETFD)&FD_CLOEXEC));
        char byte=1;assert(read(fds[0],&byte,1)==0);assert(read(fds[1],&byte,1)==1 && byte==0);
        close(fds[0]);close(fds[1]);close(s[1]);_exit(0);
    }
    close(s[1]);assert(buffer_send001(s[0],&p,original)==0);
    for(int i=0;i<3;++i)close(original[i]);
    close(s[0]);
    int status;assert(waitpid(child,&status,0)==child && WIFEXITED(status) && WEXITSTATUS(status)==0);
    original[0]=open("/dev/null",O_RDONLY|O_CLOEXEC);original[1]=dup(original[0]);original[2]=dup(original[0]);
    for(int which=0;which<6;++which) {
        assert(socketpair(AF_UNIX,SOCK_SEQPACKET|SOCK_CLOEXEC,0,s)==0);
        struct buffer_packet001 bad=p;
        if(which==2)bad.stride=1;
        if(which==4)bad.modifier=1;
        int oversized[12];for(int i=0;i<12;++i)oversized[i]=original[0];
        raw_send(s[0],&bad,which==5?oversized:original,which==0?1:which==1?3:which==5?12:2,which==3);
        int before=descriptors(),fds[2]={-1,-1};struct buffer_packet001 received={0};
        assert(buffer_recv001(s[1],&received,fds)==-1);
        assert(fds[0]==-1 && fds[1]==-1 && descriptors()==before);
        close(s[0]);close(s[1]);
    }
    for(int i=0;i<3;++i)close(original[i]);
    puts("PASS: genuine cross-process FD ownership/CLOEXEC; malformed packet/count rejection without leaks; GPU_NOT_TESTED=1");
    return 0;
}
'''
payload='source='+repr(source)+'\n'+r'''
from pathlib import Path
import subprocess,tempfile
with tempfile.TemporaryDirectory(prefix='buffer-ipc001-') as directory:
    p=Path(directory);(p/'test.c').write_text(source)
    subprocess.run(['cc','-std=gnu11','-O2','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True)
    subprocess.run([str(p/'test')],check=True,timeout=10)
'''
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=40)
    raise SystemExit(r.returncode)
