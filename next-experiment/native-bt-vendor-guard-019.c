/* Guard the SDK virtio transport; never pretend it is a native QCA controller. */
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <sys/stat.h>
#include <unistd.h>
#include "ohos_bt_vendor_abi.h"

static void *library;
static const BtVendorInterfaceT *original;

static int unavailable(const char *reason)
{
    int saved=errno;
    int fd=open("/dev/kmsg",O_WRONLY|O_CLOEXEC);
    if(fd>=0){dprintf(fd,"<3>NATIVE_BT019 unavailable reason=%s errno=%d uid=%u success_callback=0\n",reason,saved,(unsigned)getuid());close(fd);}
    errno=saved;return -1;
}

static int initialize(const BtVendorCallbacksT *callbacks,unsigned char *address)
{
    struct stat st;
    if(lstat("/dev/hwbt",&st))return unavailable("missing_virtio_transport");
    if(!S_ISCHR(st.st_mode)){errno=ENODEV;return unavailable("not_a_character_transport");}
    int fd=open("/dev/hwbt",O_RDWR|O_CLOEXEC|O_NOFOLLOW|O_NONBLOCK);
    if(fd<0)return unavailable("transport_open_failed");
    close(fd);
    if(!library)library=dlopen("/vendor/lib64/harmony-graphics/libbt_vendor-sdk-original.so",RTLD_NOW|RTLD_LOCAL);
    if(!library){errno=ELIBBAD;return unavailable("original_library_unavailable");}
    original=dlsym(library,"BLUETOOTH_VENDOR_LIB_INTERFACE");
    if(!original || original->size<sizeof(*original) || !original->init || !original->op || !original->close){
        original=NULL;errno=ELIBBAD;return unavailable("original_interface_invalid");
    }
    return original->init(callbacks,address);
}

static int operation(BtOpcodeT opcode,void *parameter)
{
    if(!original){errno=ENODEV;return unavailable("initialization_not_completed");}
    return original->op(opcode,parameter);
}

static void cleanup(void)
{
    if(original)original->close();
    original=NULL;
    if(library)dlclose(library);
    library=NULL;
}

__attribute__((visibility("default")))
const BtVendorInterfaceT BLUETOOTH_VENDOR_LIB_INTERFACE={
    .size=sizeof(BtVendorInterfaceT),.init=initialize,.op=operation,.close=cleanup,
};
