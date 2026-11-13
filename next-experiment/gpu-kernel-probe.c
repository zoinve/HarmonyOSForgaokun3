/* Throwaway, diskless ARM/KVM diagnostic; never mounts HarmonyOS disks. */
#include <dirent.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/reboot.h>
#include <sys/stat.h>
#include <unistd.h>

static void show(const char *path)
{
    FILE *f = fopen(path, "r");
    if (!f) return;
    char buf[4096];
    size_t n = fread(buf, 1, sizeof(buf) - 1, f);
    buf[n] = 0;
    printf("GPU_PROBE_FILE %s\n%s\n", path, buf);
    fclose(f);
}

int main(void)
{
    setvbuf(stdout, NULL, _IONBF, 0);
    mkdir("/proc", 0555); mkdir("/sys", 0555); mkdir("/dev", 0755);
    mount("proc", "/proc", "proc", 0, NULL);
    mount("sysfs", "/sys", "sysfs", 0, NULL);
    mount("devtmpfs", "/dev", "devtmpfs", 0, NULL);
    mount("debugfs", "/sys/kernel/debug", "debugfs", 0, NULL);
    puts("GPU_PROBE_DISKLESS_ENTER");
    for (int i = 0; i < 100 && access("/dev/dri/renderD128", F_OK); ++i)
        usleep(100000);
    printf("GPU_PROBE_RENDER_NODE present=%d\n", !access("/dev/dri/renderD128", F_OK));
    for (int card = 0; card < 4; ++card) {
        char base[128];
        snprintf(base, sizeof(base), "/sys/kernel/debug/dri/%d", card);
        DIR *d = opendir(base);
        if (!d) continue;
        struct dirent *entry;
        while ((entry = readdir(d))) {
            if (!strcmp(entry->d_name, "name") || strstr(entry->d_name, "feature")) {
                char path[512];
                snprintf(path, sizeof(path), "%s/%s", base, entry->d_name);
                show(path);
            }
        }
        closedir(d);
    }
    puts("GPU_PROBE_DISKLESS_DONE desktop_not_tested=1");
    sync();
    reboot(RB_POWER_OFF);
    for (;;) pause();
}
