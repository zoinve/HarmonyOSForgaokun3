/* Pure QCA H4 adapter; Linux owns real firmware, power and UART flow control. */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <sys/un.h>
#include <unistd.h>
#include "ohos_bt_vendor_abi.h"
static const BtVendorCallbacksT *callbacks;
static int channel=-1;
static void trace(const char *operation,int result)
{
    int saved=errno;int fd=open("/data/native-bt-020.trace",O_WRONLY|O_APPEND|O_CLOEXEC|O_NOFOLLOW);
    if(fd>=0){dprintf(fd,"NATIVE_BT022 op=%s result=%d errno=%d uid=%u\n",operation,result,result<0?saved:0,(unsigned)getuid());close(fd);}
    errno=saved;
}
static int power_on(void)
{
    if(channel>=0)return 0;
    int fd=socket(AF_UNIX,SOCK_STREAM|SOCK_CLOEXEC,0);if(fd<0)return -1;
    struct sockaddr_un address={.sun_family=AF_UNIX};
    strcpy(address.sun_path,"/vendor/lib64/harmony-graphics/native-bt-broker.sock");
    if(connect(fd,(struct sockaddr *)&address,sizeof(address)))goto fail;
    struct ucred peer;socklen_t len=sizeof(peer);
    if(getsockopt(fd,SOL_SOCKET,SO_PEERCRED,&peer,&len) || peer.uid!=0){errno=EPERM;goto fail;}
    struct timeval timeout={.tv_sec=20};
    if(setsockopt(fd,SOL_SOCKET,SO_RCVTIMEO,&timeout,sizeof(timeout)))goto fail;
    unsigned char ack;
    if(recv(fd,&ack,1,MSG_WAITALL)!=1 || ack!=0){errno=ENODEV;goto fail;}
    timeout.tv_sec=0;
    if(setsockopt(fd,SOL_SOCKET,SO_RCVTIMEO,&timeout,sizeof(timeout)))goto fail;
    channel=fd;trace("real_power_on",0);return 0;
fail:{int saved=errno;close(fd);errno=saved;trace("real_power_on",-1);return -1;}
}
static void power_off(void){if(channel>=0){close(channel);channel=-1;}trace("real_power_off",0);}
static int initialize(const BtVendorCallbacksT *cb,unsigned char *address)
{
    (void)address;
    if(!cb || cb->size<sizeof(*cb) || !cb->initCb){errno=EINVAL;return -1;}
    callbacks=cb;return 0;
}
static int operation(BtOpcodeT opcode,void *parameter)
{
    if(!callbacks){errno=ENODEV;return -1;}
    switch(opcode){
    case BT_OP_POWER_ON:return power_on();
    case BT_OP_POWER_OFF:case BT_OP_HCI_CHANNEL_CLOSE:power_off();return 0;
    case BT_OP_HCI_CHANNEL_OPEN:
        if(!parameter || channel<0){errno=ENODEV;return -1;}
        for(unsigned i=0;i<HCI_MAX_CHANNEL;++i)((int *)parameter)[i]=channel;
        trace("h4_channel_open",1);return 1;
    case BT_OP_INIT:
        if(channel<0){errno=ENODEV;return -1;}
        /* Broker acknowledges only a successful real HCI_USER bind/setup. */
        callbacks->initCb(BTC_OP_RESULT_SUCCESS);trace("real_firmware_initialized",0);return 0;
    default:errno=ENOTSUP;trace("unsupported_operation",-1);return -1;
    }
}
static void cleanup(void){power_off();callbacks=NULL;}
__attribute__((visibility("default")))
const BtVendorInterfaceT BLUETOOTH_VENDOR_LIB_INTERFACE={sizeof(BtVendorInterfaceT),initialize,operation,cleanup};
