#ifndef SDK_DISK_SELECTION_035_H
#define SDK_DISK_SELECTION_035_H
#include <dirent.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>

/* Read-only discovery. 1=unique serial+capacity match, 0=not present, -1=unsafe. */
static int sdk_select_disk_035(const char *root, const char *serial,
                               unsigned long long sectors, char *name, size_t size)
{
    DIR *dir = opendir(root);
    if (!dir) return 0;
    unsigned matches = 0, scanned = 0;
    int result = 0;
    struct dirent *entry;
    while ((entry = readdir(dir))) {
        if (strncmp(entry->d_name, "vd", 2)) continue;
        if (++scanned > 64) { result = -1; break; }
        char path[1024], observed[256];
        int n = snprintf(path, sizeof(path), "%s/%s/serial", root, entry->d_name);
        if (n < 0 || (size_t)n >= sizeof(path)) { result = -1; break; }
        FILE *f = fopen(path, "r");
        if (!f) continue;
        int ok = fgets(observed, sizeof(observed), f) != NULL;
        fclose(f);
        if (!ok) continue;
        observed[strcspn(observed, "\r\n")] = 0;
        if (strcmp(serial, observed)) continue;
        if (++matches != 1 || strlen(entry->d_name) >= size) { result = -1; break; }
        n = snprintf(path, sizeof(path), "%s/%s/size", root, entry->d_name);
        if (n < 0 || (size_t)n >= sizeof(path)) { result = -1; break; }
        f = fopen(path, "r");
        if (!f) { result = -1; break; }
        ok = fgets(observed, sizeof(observed), f) != NULL;
        fclose(f);
        char *end = NULL;
        errno = 0;
        unsigned long long capacity = ok ? strtoull(observed, &end, 10) : 0;
        if (!ok || errno || end == observed || strspn(end, "\r\n") != strlen(end) || capacity != sectors) {
            result = -1; break;
        }
        strcpy(name, entry->d_name);
        result = 1;
    }
    closedir(dir);
    return result;
}
#endif
