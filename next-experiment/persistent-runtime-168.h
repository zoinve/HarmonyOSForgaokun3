#ifndef PERSISTENT_RUNTIME_168_H
#define PERSISTENT_RUNTIME_168_H
#include "persistent-runtime-166.h"

static void persistent_runtime168(void)
{
    persistent_runtime166();
    char boot[80];
    if (read_path("/proc/sys/kernel/random/boot_id",boot,sizeof(boot)) != 37 || boot[36] != '\n')
        fail("persistent memory history boot");
    boot[36]=0;
    int root=open("/data/.harmony-persistent166",O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
    int history=root<0?-1:openat(root,boot,O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
    int datadir=open("/data",O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
    if (root<0 || history<0 || datadir<0) fail("persistent memory history directory");
    struct stat st;
    int present=0;
    if (!fstatat(datadir,"commercial-memmgr108.log",&st,AT_SYMLINK_NOFOLLOW)) {
        if (!S_ISREG(st.st_mode) || st.st_uid ||
            renameat(datadir,"commercial-memmgr108.log",history,"commercial-memmgr108.log"))
            fail("persistent memory history archive");
        present=1;
    } else if (errno != ENOENT) fail("persistent memory history stat");
    if (fsync(history) || close(history) || fsync(datadir) || close(datadir) ||
        fsync(root) || syncfs(root) || close(root)) fail("persistent memory history sync");
    dprintf(1,"PERSISTENT168_MEMORY_ARCHIVE previous_log_present=%d preserved=1\n",present);
}
#endif
