#include <stddef.h>

struct identity091_facts {
    int existing_valid;
    int api_ok;
    int existing_nonempty;
    int hardware_ok;
    int metadata_match;
    int serial_present;
    int serial_match;
};

enum identity091_action {
    ID091_PRESERVE = 0,
    ID091_ORIGINAL_MODULE = 1,
    ID091_SUPPLY_SERIAL = 2,
    ID091_API_ERROR = 10,
    ID091_EXISTING_INVALID = 11,
    ID091_HARDWARE_ERROR = 12,
    ID091_METADATA_CONFLICT = 13,
    ID091_SERIAL_CONFLICT = 14
};

static enum identity091_action identity091_decide(struct identity091_facts f)
{
    if (f.existing_valid) return ID091_PRESERVE;
    if (!f.api_ok) return ID091_API_ERROR;
    if (f.existing_nonempty) return ID091_EXISTING_INVALID;
    if (!f.hardware_ok) return ID091_HARDWARE_ERROR;
    if (!f.metadata_match) return ID091_METADATA_CONFLICT;
    if (f.serial_present && !f.serial_match) return ID091_SERIAL_CONFLICT;
    return f.serial_present ? ID091_ORIGINAL_MODULE : ID091_SUPPLY_SERIAL;
}

#ifndef HARDWARE091_TEST
#include <ctype.h>
#include <dlfcn.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/vfs.h>
#include <unistd.h>

static int firmware091_read(const char *path, char *out, size_t size)
{
    int fd = open(path, O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    struct stat st;
    struct statfs fs;
    if (fd < 0) return -1;
    if (fstat(fd, &st) || !S_ISREG(st.st_mode) || fstatfs(fd, &fs) ||
        (unsigned long)fs.f_type != 0x62656572UL) {
        close(fd);
        return -1;
    }
    ssize_t n = read(fd, out, size - 1);
    close(fd);
    if (n <= 0 || (size_t)n >= size - 1) return -1;
    while (n > 0 && (out[n-1] == '\n' || out[n-1] == '\r' || out[n-1] == '\0' || out[n-1] == ' ')) --n;
    out[n] = '\0';
    return n > 0 ? 0 : -1;
}

static int serial091_valid(const char *value)
{
    if (strlen(value) != 16) return 0;
    int varied = 0;
    for (size_t i = 0; value[i]; ++i) {
        if (!isalnum((unsigned char)value[i])) return 0;
        if (value[i] != value[0]) varied = 1;
    }
    return varied;
}

static int udid091_valid(int result, const char *value)
{
    if (result != 0 || strlen(value) != 64) return 0;
    for (size_t i = 0; value[i]; ++i)
        if (!isxdigit((unsigned char)value[i])) return 0;
    return 1;
}

static int target091_valid(void)
{
    char name[32] = {0};
    int fd = open("/proc/1/comm", O_RDONLY | O_CLOEXEC);
    if (fd < 0) return 0;
    ssize_t n = read(fd, name, sizeof(name) - 1);
    close(fd);
    struct stat hap;
    return n == 5 && !memcmp(name, "init\n", 5) && getuid() == 0 &&
        !stat("/system/app/SceneBoard/SceneBoard.hap", &hap) && hap.st_size == 87269511;
}

int main(int argc, char **argv)
{
    if (argc != 2 || strcmp(argv[1], "--supply-physical-serial") || !target091_valid()) {
        puts("HARDWARE091_REFUSED reason=not_original_target_or_opt_in");
        return 64;
    }
    void *library = dlopen("/system/lib64/chipset-sdk-sp/libbegetutil.z.so", RTLD_NOW | RTLD_GLOBAL);
    int (*get)(const char *, const char *, char *, unsigned int) = library ? dlsym(library, "GetParameter") : NULL;
    int (*set)(const char *, const char *) = library ? dlsym(library, "SetParameter") : NULL;
    int (*udid)(char *, int) = library ? dlsym(library, "GetDevUdid") : NULL;
    if (!get || !set || !udid) {
        puts("HARDWARE091_REFUSED reason=original_api_missing");
        return 65;
    }
    const char *keys[] = {"ohos.boot.sn", "const.product.udid", "const.product.devUdid",
                          "const.product.manufacturer", "const.product.model"};
    char values[5][256] = {{0}};
    int api_ok = 1;
    for (unsigned i = 0; i < 5; ++i) {
        int result = get(keys[i], "", values[i], sizeof(values[i]));
        values[i][sizeof(values[i])-1] = '\0';
        if (result < 0) api_ok = 0;
        printf("HARDWARE091_PARAMETER key=%s return=%d length=%zu value_exported=0\n", keys[i], result, strlen(values[i]));
    }
    char before[256] = {0};
    int initial = udid(before, sizeof(before));
    before[sizeof(before)-1] = '\0';
    int valid = udid091_valid(initial, before);
    printf("HARDWARE091_GETDEVUDID phase=before return=%d length=%zu valid_hex64=%d value_exported=0\n", initial, strlen(before), valid);
    char serial[128] = {0}, chassis[128] = {0}, vendor[128] = {0}, model[128] = {0};
    int hardware_ok = !firmware091_read("/sys/class/dmi/id/product_serial", serial, sizeof(serial)) &&
        !firmware091_read("/sys/class/dmi/id/chassis_serial", chassis, sizeof(chassis)) &&
        !firmware091_read("/sys/class/dmi/id/sys_vendor", vendor, sizeof(vendor)) &&
        !firmware091_read("/sys/class/dmi/id/product_name", model, sizeof(model)) &&
        serial091_valid(serial) && !strcmp(serial, chassis) && vendor[0] && model[0];
    int metadata_match = hardware_ok && !strcmp(values[3], vendor) && !strcmp(values[4], model);
    int serial_match = hardware_ok && !strcmp(values[0], serial);
    printf("HARDWARE091_FIRMWARE readable_valid_matching_serials=%d serial_length=%zu manufacturer_matches=%d model_matches=%d boot_serial_matches=%d value_exported=0\n",
        hardware_ok, hardware_ok ? strlen(serial) : 0,
        hardware_ok && !strcmp(values[3], vendor), hardware_ok && !strcmp(values[4], model), serial_match);
    struct identity091_facts facts = {valid, api_ok, values[1][0] || values[2][0],
                                     hardware_ok, metadata_match, !!values[0][0], serial_match};
    enum identity091_action action = identity091_decide(facts);
    printf("HARDWARE091_DECISION action=%d preserve_existing_identity=1 no_generated_replacement=1\n", action);
    if (action == ID091_PRESERVE) {
        puts("HARDWARE091_EXISTING_VALID no_write_requested=1");
        return 0;
    }
    if (action >= ID091_API_ERROR) {
        printf("HARDWARE091_REFUSED reason_code=%d no_write_requested=1\n", action);
        return action;
    }
    if (action == ID091_SUPPLY_SERIAL) {
        int result = set("ohos.boot.sn", serial);
        printf("HARDWARE091_SERIAL_SUPPLY original_public_api=1 return=%d firmware_value_only=1\n", result);
        if (result != 0) return 66;
        char observed[256] = {0};
        result = get("ohos.boot.sn", "", observed, sizeof(observed));
        observed[sizeof(observed)-1] = '\0';
        int matches = result >= 0 && !strcmp(observed, serial);
        printf("HARDWARE091_SERIAL_RECHECK matches_firmware=%d value_exported=0\n", matches);
        if (!matches) return 67;
    }
    void *module = dlopen("/system/lib64/init/libudidmodule.z.so", RTLD_NOW | RTLD_LOCAL);
    printf("HARDWARE091_ORIGINAL_MODULE loaded=%d original_calculation_only=1\n", module != NULL);
    if (!module) return 68;
    char after[256] = {0};
    int result = udid(after, sizeof(after));
    after[sizeof(after)-1] = '\0';
    valid = udid091_valid(result, after);
    printf("HARDWARE091_GETDEVUDID phase=after return=%d length=%zu valid_hex64=%d value_exported=0\n", result, strlen(after), valid);
    return valid ? 0 : 69;
}
#endif
