#define _GNU_SOURCE
#include <dlfcn.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <unistd.h>

/* Public libusb 1.0 C API; opaque types do not import platform C++ objects.
 * Declarations checked against libusb/libusb v1.0.27, libusb/libusb.h. */
typedef struct libusb_context USB153Context;
typedef struct libusb_device USB153Device;
struct usb153_api {
    int (*init)(USB153Context **);
    void (*exit)(USB153Context *);
    ssize_t (*list)(USB153Context *, USB153Device ***);
    void (*free_list)(USB153Device **, int);
    uint8_t (*bus)(USB153Device *);
    uint8_t (*address)(USB153Device *);
};

static int usb153_enumerate(const struct usb153_api *api)
{
    USB153Context *context = NULL;
    int status = api->init(&context);
    printf("USB153_INIT status=%d backend_only=1\n", status);
    if (status < 0) return 80;
    if (!context) {
        printf("USB153_REFUSED reason=null_context\n");
        api->exit(context);
        return 81;
    }
    USB153Device **devices = NULL;
    ssize_t count = api->list(context, &devices);
    printf("USB153_LIST count=%zd backend_only=1 service_acceptance_not_inferred=1\n", count);
    int result = 0;
    if (count < 0 || count > 128 || (count > 0 && !devices)) {
        printf("USB153_REFUSED reason=list_error_or_limit\n");
        result = 82;
    } else {
        for (ssize_t i = 0; i < count; ++i) {
            if (!devices[i]) {
                printf("USB153_REFUSED reason=missing_list_member\n");
                result = 83;
                break;
            }
            unsigned bus = api->bus(devices[i]), address = api->address(devices[i]);
            if (!bus || !address || address > 127) {
                printf("USB153_REFUSED reason=invalid_bus_or_address\n");
                result = 84;
                break;
            }
            printf("USB153_DEVICE bus=%u address=%u node=/dev/bus/usb/%03u/%03u\n", bus, address, bus, address);
        }
    }
    if (devices) api->free_list(devices, 1);
    api->exit(context);
    printf("USB153_END status=%d configuration_changed=0 interfaces_claimed=0 serials_read=0\n", result);
    return result;
}

#ifndef USB153_NO_MAIN
static int usb153_read(const char *path, char *text, size_t capacity)
{
    int fd = open(path, O_RDONLY | O_NOFOLLOW | O_CLOEXEC);
    if (fd < 0) return 0;
    ssize_t count = read(fd, text, capacity - 1);
    close(fd);
    if (count <= 0 || count >= (ssize_t)capacity - 1) return 0;
    text[count] = 0;
    return 1;
}

int main(int argc, char **argv)
{
    char model[128], command[8192];
    if (argc != 2 || strcmp(argv[1], "--enumerate-original-backend") || getuid() != 0 ||
        access("/system/bin/sa_main", X_OK) ||
        !usb153_read("/sys/firmware/devicetree/base/model", model, sizeof(model)) || !strstr(model, "Matebook E Go") ||
        !usb153_read("/proc/cmdline", command, sizeof(command)) || !strstr(command, "harmony.commercial=1") ||
        !strstr(command, "harmony.native_original=1")) {
        fprintf(stderr, "USB153_REFUSED reason=native_board_root_and_optin_required\n");
        return 77;
    }
    void *library = dlopen("/system/lib64/chipset-sdk-sp/libusb_shared.z.so", RTLD_NOW | RTLD_LOCAL);
    if (!library) {
        printf("USB153_REFUSED reason=original_library_load_failed\n");
        return 78;
    }
    struct usb153_api api = {
        .init = (int (*)(USB153Context **))dlsym(library, "libusb_init"),
        .exit = (void (*)(USB153Context *))dlsym(library, "libusb_exit"),
        .list = (ssize_t (*)(USB153Context *, USB153Device ***))dlsym(library, "libusb_get_device_list"),
        .free_list = (void (*)(USB153Device **, int))dlsym(library, "libusb_free_device_list"),
        .bus = (uint8_t (*)(USB153Device *))dlsym(library, "libusb_get_bus_number"),
        .address = (uint8_t (*)(USB153Device *))dlsym(library, "libusb_get_device_address")
    };
    if (!api.init || !api.exit || !api.list || !api.free_list || !api.bus || !api.address) {
        printf("USB153_REFUSED reason=required_original_symbol_absent\n");
        dlclose(library);
        return 79;
    }
    int result = usb153_enumerate(&api);
    dlclose(library);
    return result;
}
#endif
