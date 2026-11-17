#ifndef PERSISTENT_DIAGNOSTIC_HISTORY_173_H
#define PERSISTENT_DIAGNOSTIC_HISTORY_173_H
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <sys/stat.h>
#include <unistd.h>

static const char *const persistent173_logs[] = {
    "commercial-account-order063.log", "commercial-event-state064.log",
    "commercial-desktop086.log", "commercial-direct-desktop075.log",
    "commercial-server-stack104.log", "commercial-server-stack105.log",
    "commercial-server-stack107.log", "commercial-memmgr-stack109.log",
    "commercial-collaboration-ready116.log", "native-layout086-100.json",
    "native-layout086-130.json", "commercial-query107.fifo",
    "commercial-collaboration-ready116.fifo"
};

static int persistent173_archive(int data, int history, unsigned *files, unsigned *fifos)
{
    *files = *fifos = 0;
    for (unsigned i=0;i<sizeof(persistent173_logs)/sizeof(persistent173_logs[0]);++i) {
        struct stat st, existing;
        const char *name = persistent173_logs[i];
        if (fstatat(data,name,&st,AT_SYMLINK_NOFOLLOW)) {
            if (errno == ENOENT) continue;
            return -1;
        }
        int fifo = i >= 11;
        if (st.st_nlink != 1 || (fifo ? !S_ISFIFO(st.st_mode) : !S_ISREG(st.st_mode))) return -1;
        if (!fstatat(history,name,&existing,AT_SYMLINK_NOFOLLOW) || errno != ENOENT) return -1;
        if (renameat(data,name,history,name)) return -1;
        if (fifo) ++*fifos; else ++*files;
    }
    return fsync(history) || fsync(data) ? -1 : 0;
}
#endif
