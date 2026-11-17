#ifndef COMMERCIAL_MEMMGR_PREREQUISITES_108_H
#define COMMERCIAL_MEMMGR_PREREQUISITES_108_H

#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <sys/stat.h>
#include <unistd.h>

#ifndef MEMMGR108_ROOT
#define MEMMGR108_ROOT ""
#endif

static void commercial_memmgr108(void)
{
    const char *log108 = MEMMGR108_ROOT "/data/commercial-memmgr108.log";
    const char *paths108[] = {
        MEMMGR108_ROOT "/data/local",
        MEMMGR108_ROOT "/data/local/tmp",
        MEMMGR108_ROOT "/data/local/tmp/memmgr-nohyperhold-v1",
        MEMMGR108_ROOT "/data/local/tmp/memmgr-nohyperhold-v1/memcg",
        MEMMGR108_ROOT "/dev/memcg"
    };
    int fd108 = open(log108, O_WRONLY | O_CREAT | O_EXCL | O_CLOEXEC | O_NOFOLLOW, 0600);
    if (fd108 < 0) fail("memory prerequisite evidence 108");
    dprintf(fd108, "MEMMGR108_PREINIT_BEGIN directories_only=1 fake_metrics=0 original_launch_chain=1\n");
    for (unsigned i108 = 0; i108 < sizeof(paths108) / sizeof(paths108[0]); ++i108) {
        struct stat st108;
        int present108 = lstat(paths108[i108], &st108) == 0;
        int error108 = present108 ? 0 : errno;
        dprintf(fd108, "MEMMGR108_PATH_BEFORE path=%s present=%d errno=%d\n", paths108[i108], present108, error108);
        if (!present108) {
            if (error108 != ENOENT || mkdir(paths108[i108], 0755) || lstat(paths108[i108], &st108)) {
                dprintf(fd108, "MEMMGR108_REFUSED path=%s errno=%d\n", paths108[i108], errno);
                fsync(fd108);
                fail("memory prerequisite directory 108");
            }
        }
        if (!S_ISDIR(st108.st_mode) || S_ISLNK(st108.st_mode)) {
            dprintf(fd108, "MEMMGR108_REFUSED path=%s reason=not_directory\n", paths108[i108]);
            fsync(fd108);
            fail("memory prerequisite unsafe object 108");
        }
        dprintf(fd108, "MEMMGR108_PATH_AFTER path=%s created=%d uid=%u gid=%u mode=%o\n",
                paths108[i108], !present108, st108.st_uid, st108.st_gid, st108.st_mode & 07777);
    }
    dprintf(fd108, "MEMMGR108_PREINIT_END service_success_not_inferred=1\n");
    if (fsync(fd108) || close(fd108)) fail("memory prerequisite evidence sync 108");
    dprintf(1, "COMMERCIAL108_MEMORY_PREREQUISITES directories_only=1 fake_metrics=0 original_wrappers_unchanged=1\n");
}

#endif
