"""Separate exec'd consumer receives DMA-BUF and native sync_file; no display/KMS access."""
from pathlib import Path
import runpy

def build_source():
    base=Path(__file__).resolve().parent
    source=runpy.run_path(str(base/'baremetal-freedreno-fence-probe-001.py'))['build_source']()
    helper=r'''
#include "baremetal-buffer-ipc-001.h"
#include <sys/wait.h>
#include <sys/syscall.h>
#include <limits.h>
#include <errno.h>
struct consumer_ack001 { int32_t pid,status; unsigned char center[4],background[4]; };
static int consume001(void)
{
    struct buffer_packet001 packet={0};int fds[2];
    require(buffer_recv001(3,&packet,fds)==0 && packet.width==16 && packet.height==16,
            "consumer receives exact two FD packet");
    require((fcntl(fds[0],F_GETFD)&FD_CLOEXEC) && (fcntl(fds[1],F_GETFD)&FD_CLOEXEC),
            "received FD close-on-exec ownership");
    struct pollfd pending={.fd=fds[1],.events=POLLIN};
    int polled=poll(&pending,1,3000);
    require(polled==1 && (pending.revents&POLLIN) &&
            !(pending.revents&(POLLERR|POLLHUP|POLLNVAL)),"consumer explicit native fence wait");
    close(fds[1]);
    int render=open("/dev/dri/renderD128",O_RDWR|O_CLOEXEC);
    require(render>=0,"consumer independent render open");
    struct gbm_device *device=gbm_create_device(render);require(device!=NULL,"consumer GBM device");
    struct gbm_import_fd_modifier_data data={.width=packet.width,.height=packet.height,
        .format=packet.format,.num_fds=1,.fds={fds[0]},.strides={(int)packet.stride},
        .offsets={0},.modifier=0};
    struct gbm_bo *bo=gbm_bo_import(device,GBM_BO_IMPORT_FD_MODIFIER,&data,GBM_BO_USE_RENDERING);
    require(bo!=NULL,"exec consumer DMA-BUF import");
    close(fds[0]); /* Imported BO must retain its own reference. */
    uint32_t stride=0;void *map_data=NULL;
    unsigned char *pixels=gbm_bo_map(bo,0,0,16,16,GBM_BO_TRANSFER_READ,&stride,&map_data);
    require(pixels!=NULL && stride>=64,"consumer CPU map after fence");
    unsigned char *c=pixels+8*stride+8*4,*b=pixels+8*stride;
    struct consumer_ack001 ack={.pid=getpid(),.status=0,
        .center={c[2],c[1],c[0],c[3]},.background={b[2],b[1],b[0],b[3]}};
    require(freedreno_pixels_ok(ack.center,ack.background),"exec consumer actual GPU pixels");
    printf("IPC001_CONSUMER pid=%d fence_poll=%d center=%u,%u,%u,%u background=%u,%u,%u,%u imported_fd_closed=1\n",
        ack.pid,polled,ack.center[0],ack.center[1],ack.center[2],ack.center[3],
        ack.background[0],ack.background[1],ack.background[2],ack.background[3]);
    gbm_bo_unmap(bo,map_data);gbm_bo_destroy(bo);gbm_device_destroy(device);close(render);
    require(send(3,&ack,sizeof(ack),MSG_NOSIGNAL)==(ssize_t)sizeof(ack),"consumer acknowledgement");
    close(3);return 0;
}
'''
    assert source.count('int main(void)')==1
    source=source.replace('int main(void)',helper+'\nint main(int argc,char **argv)')
    anchor='    setvbuf(stdout, NULL, _IONBF, 0);'
    assert source.count(anchor)==1
    source=source.replace(anchor,anchor+r'''
    if(argc==2 && !strcmp(argv[1],"--receive-fd3"))return consume001();
    require(argc==1,"producer arguments");
    int transport[2];
    require(socketpair(AF_UNIX,SOCK_SEQPACKET|SOCK_CLOEXEC,0,transport)==0,"private FD channel");
    pid_t consumer=fork();require(consumer>=0,"fork consumer before GPU initialization");
    if(!consumer) {
        close(transport[0]);
        if(transport[1]!=3)require(dup2(transport[1],3)==3,"consumer socket descriptor");
        require(fcntl(3,F_SETFD,0)==0,"keep only consumer channel across exec");
        require(syscall(SYS_close_range,4u,~0u,0u)==0,"close inherited non-channel descriptors");
        char loader[PATH_MAX],lib[PATH_MAX];const char *slash=strrchr(argv[0],'/');
        require(slash!=NULL && (size_t)(slash-argv[0])<PATH_MAX-64,"absolute private executable path");
        int n=(int)(slash-argv[0]);
        require(snprintf(loader,sizeof(loader),"%.*s/lib/ld-musl-aarch64.so.1",n,argv[0])<PATH_MAX &&
                snprintf(lib,sizeof(lib),"%.*s/lib",n,argv[0])<PATH_MAX,"consumer loader paths");
        execl(loader,loader,"--library-path",lib,argv[0],"--receive-fd3",(char *)NULL);
        require(0,"exec consumer with original OHOS loader");
    }
    close(transport[1]);
''')
    anchor='    require(fence_fd >= 0, "export sync_file fd");'
    assert source.count(anchor)==1
    source=source.replace(anchor,anchor+r'''
    struct buffer_packet001 packet={.magic=0x42464631,.width=width,.height=height,
        .stride=stride,.format=GBM_FORMAT_ARGB8888,.offset=offset,.modifier=modifier};
    int outgoing[2]={dup(dma_fd),dup(fence_fd)};
    require(outgoing[0]>=0 && outgoing[1]>=0 && buffer_send001(transport[0],&packet,outgoing)==0,
            "send DMA-BUF and actual GPU sync_file");
    close(outgoing[0]);close(outgoing[1]);
    struct pollfd response={.fd=transport[0],.events=POLLIN};
    require(poll(&response,1,5000)==1 && (response.revents&POLLIN),"bounded consumer completion");
    struct consumer_ack001 ack={0};
    require(recv(transport[0],&ack,sizeof(ack),MSG_TRUNC)==(ssize_t)sizeof(ack) && ack.pid==consumer &&
            ack.status==0 && freedreno_pixels_ok(ack.center,ack.background),"separate consumer acknowledgement");
    int consumer_status=0;
    require(waitpid(consumer,&consumer_status,0)==consumer && WIFEXITED(consumer_status) &&
            WEXITSTATUS(consumer_status)==0,"consumer clean exit");
    close(transport[0]);
    printf("IPC001_TRANSFER producer=%d consumer=%d exec_consumer=1 sender_transfer_fds_closed=1 consumer_imported_fd_closed=1\n",
            getpid(),ack.pid);
''')
    source=source.replace('PASS native_fence_and_dmabuf_coherence desktop_not_tested=1',
                          'PASS cross_process_dmabuf_and_native_fence desktop_not_tested=1')
    return '#define _GNU_SOURCE\n'+source.replace('FENCE001_','IPC001_')
