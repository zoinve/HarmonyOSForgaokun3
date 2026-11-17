#ifndef PERSISTENT_DATA_172_H
#define PERSISTENT_DATA_172_H
#include <sys/vfs.h>
#include "persistent-unmount-plan-172.h"

#define persistent166_finish persistent172_legacy_finish
#include "persistent-data-166.h"
#undef persistent166_finish

static int persistent172_namespace = -1, persistent172_root = -1;
static pid_t persistent172_target = -1;
static int persistent172_target_reaped;

static void persistent172_pin(pid_t child)
{
    if (persistent166_fd < 0 || child < 2 || persistent172_target > 0) return;
    char path[128];
    snprintf(path,sizeof(path),"/proc/%d/ns/mnt",child);
    int ns = open(path,O_RDONLY|O_CLOEXEC);
    snprintf(path,sizeof(path),"/proc/%d/root",child);
    int root = open(path,O_RDONLY|O_DIRECTORY|O_CLOEXEC);
    snprintf(path,sizeof(path),"/proc/%d/root/data",child);
    int data = open(path,O_RDONLY|O_DIRECTORY|O_CLOEXEC);
    struct stat st, own, other;
    struct statfs fs;
    int ownns = open("/proc/self/ns/mnt",O_RDONLY|O_CLOEXEC);
    int failed = ns < 0 || root < 0 || data < 0 || ownns < 0 ||
        fstat(data,&st) || st.st_dev != makedev(7,3) || fstatfs(data,&fs) ||
        fs.f_type != 0xef53 || fstat(ns,&other) || fstat(ownns,&own) ||
        (own.st_dev == other.st_dev && own.st_ino == other.st_ino);
    if (ownns >= 0) close(ownns);
    if (data >= 0) close(data);
    if (failed) {
        if (ns >= 0) close(ns);
        if (root >= 0) close(root);
        dprintf(1,"PERSISTENT172_PIN_REFUSED target=%d errno=%d\n",child,errno);
        return;
    }
    persistent172_namespace = ns;
    persistent172_root = root;
    persistent172_target = child;
    dprintf(1,"PERSISTENT172_PIN target=%d data_identity_verified=1\n",child);
}

static void persistent172_reaped(pid_t target, pid_t got)
{
    persistent172_target_reaped = target == persistent172_target && got == target;
}

static int persistent172_load_plan(int procdir, struct persistent172_mount *rows, unsigned *count)
{
    int fd = openat(procdir,"mountinfo",O_RDONLY|O_CLOEXEC);
    if (fd < 0) return -1;
    FILE *stream = fdopen(fd,"r");
    if (!stream) { close(fd); return -1; }
    int result = persistent172_plan(stream,rows,count,7,3);
    if (fclose(stream)) result = -1;
    return result;
}

static void persistent172_finish_worker(void *unused)
{
    (void)unused;
    /* This proc directory identifies this worker even after changing its root. */
    int procdir = open("/proc/self",O_RDONLY|O_DIRECTORY|O_CLOEXEC);
    if (procdir < 0 || setns(persistent172_namespace,CLONE_NEWNS) ||
        fchdir(persistent172_root) || chroot(".") || chdir("/")) _exit(121);
    int data = open("/data",O_RDONLY|O_DIRECTORY|O_CLOEXEC|O_NOFOLLOW);
    struct stat st;
    if (data < 0 || fstat(data,&st) || st.st_dev != makedev(7,3) || syncfs(data) || close(data)) _exit(122);
    struct persistent172_mount *rows = calloc(PERSISTENT172_MAX_MOUNTS,sizeof(*rows));
    unsigned count = 0, removed = 0;
    if (!rows || persistent172_load_plan(procdir,rows,&count)) _exit(123);
    int index;
    while ((index = persistent172_next(rows,count)) >= 0) {
        if (umount(rows[index].path)) {
            dprintf(1,"PERSISTENT172_UNMOUNT_REFUSED mount_id=%u errno=%d\n",rows[index].id,errno);
            _exit(124);
        }
        rows[index].removed = 1;
        ++removed;
    }
    if (index != -1 || !removed || persistent172_load_plan(procdir,rows,&count)) _exit(125);
    for (unsigned i=0;i<count;++i) if (rows[i].selected) _exit(126);
    free(rows);
    if (close(procdir) || fsync(persistent166_fd) || syncfs(persistent166_fd)) _exit(127);
    dprintf(1,"PERSISTENT172_FLUSHED target_reaped=1 data_mounts_removed=%u remaining_data_mounts=0 inner_syncfs=1 backing_fsync=1 outer_syncfs=1\n",removed);
}

static void persistent172_finish(void)
{
    /* The inherited remount-only finish remains unused; there is no fallback. */
    (void)persistent172_legacy_finish;
    if (persistent166_fd < 0) return;
    int result = -1;
    if (persistent172_namespace >= 0 && persistent172_root >= 0 && persistent172_target_reaped)
        result = commercial_bounded010(persistent172_finish_worker,NULL,12000);
    dprintf(1,"PERSISTENT172_FINISH status=%d target_reaped=%d original_services_graceful_shutdown=0\n",result,persistent172_target_reaped);
    if (persistent172_namespace >= 0) close(persistent172_namespace);
    if (persistent172_root >= 0) close(persistent172_root);
    close(persistent166_fd);
    persistent166_fd = persistent172_namespace = persistent172_root = -1;
}
#endif
