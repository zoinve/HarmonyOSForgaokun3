#define _GNU_SOURCE
#include <dirent.h>
#include <dlfcn.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

/* Exact C array layout also witnessed in the pinned original SAMGR consumer.
 * This diagnostic is NOT SAMGR and never invokes its private parser or services. */
struct CfgFiles { char *paths[32]; };

int main(void)
{
    char cmdline[4096] = {0};
    int fd = open("/proc/cmdline", O_RDONLY | O_CLOEXEC);
    ssize_t got = fd < 0 ? -1 : read(fd, cmdline, sizeof(cmdline) - 1);
    if (fd >= 0) close(fd);
    if (got <= 0 || !strstr(cmdline, "harmony.original_init_test=1") ||
        !strstr(cmdline, "enforcing=0") || getpid() == 1) return 77;
    alarm(8);
    printf("CONFIG_QUERY caller_uid=%u diagnostic_caller_not_samgr=1 read_only=1\n",
           (unsigned)getuid());
    void *lib = dlopen("/system/lib64/chipset-sdk-sp/libconfigpolicy_util.z.so", RTLD_NOW | RTLD_LOCAL);
    if (!lib) { printf("CONFIG_QUERY dlopen_error=%s\n", dlerror()); return 70; }
    struct CfgFiles *(*get)(const char *) = (struct CfgFiles *(*)(const char *))dlsym(lib, "GetCfgFiles");
    void (*release)(struct CfgFiles *) = (void (*)(struct CfgFiles *))dlsym(lib, "FreeCfgFiles");
    if (!get || !release) { puts("CONFIG_QUERY missing_original_api=1"); return 70; }
    struct CfgFiles *files = get("profile");
    if (!files) { puts("CONFIG_QUERY null_result=1"); return 70; }
    for (unsigned i = 0; i < 32; ++i) {
        if (!files->paths[i]) continue;
        printf("CONFIG_QUERY slot=%u path=%s\n", i, files->paths[i]);
        DIR *dir = opendir(files->paths[i]);
        unsigned count = 0, json_count = 0;
        if (dir) {
            struct dirent *entry;
            while (count < 512 && (entry = readdir(dir))) {
                ++count;
                size_t len = strlen(entry->d_name);
                if (len >= 5 && !strcmp(entry->d_name + len - 5, ".json")) ++json_count;
            }
            closedir(dir);
        }
        printf("CONFIG_QUERY slot=%u directory_open=%u entries=%u json=%u\n", i, dir != NULL, count, json_count);
        char path[4096], body[641] = {0};
        int length = snprintf(path, sizeof(path), "%s/installs.json", files->paths[i]);
        if (length < 0 || (size_t)length >= sizeof(path)) continue;
        fd = open(path, O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
        got = fd < 0 ? -1 : read(fd, body, sizeof(body) - 1);
        int error = got < 0 ? errno : 0;
        if (fd >= 0) close(fd);
        printf("CONFIG_QUERY slot=%u installs_bytes=%ld errno=%d body=%s\n", i, (long)got, error, body);
    }
    release(files);
    dlclose(lib);
    return 0;
}
