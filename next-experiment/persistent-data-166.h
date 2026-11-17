#ifndef PERSISTENT_DATA_166_H
#define PERSISTENT_DATA_166_H
#include <sys/file.h>

static int persistent166_fd = -1;
static int persistent166_prepare(void)
{
    char command[8192];
    if (read_text("/proc/cmdline",command,sizeof(command)) ||
        !strstr(command," harmony.persistent_data166=1")) return -1;
    int root = open("/mnt/lab",O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
    struct stat partition, mounted_stat, folder, file;
    if (root < 0 || stat("/dev/nvme0n1p4",&partition) || fstat(root,&mounted_stat) ||
        mounted_stat.st_dev != partition.st_rdev) {
        if (root >= 0) close(root);
        return -1;
    }
    int dir = openat(root,"harmony-persistent-data-165",O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
    close(root);
    if (dir < 0) return -1;
    int fd = openat(dir,"data.ext4",O_RDWR|O_NOFOLLOW|O_CLOEXEC);
    int failed = fstat(dir,&folder) || folder.st_uid || (folder.st_mode & 0777) != 0700 ||
        fd < 0 || fstat(fd,&file) || !S_ISREG(file.st_mode) || file.st_uid ||
        (file.st_mode & 0777) != 0600 || file.st_nlink != 1 ||
        file.st_dev != mounted_stat.st_dev || file.st_size != 8589934592LL ||
        (unsigned long long)file.st_blocks*512 < 8589934592ULL;
    close(dir);
    unsigned char super[120];
    static const unsigned char uuid[16] = PERSISTENT166_UUID;
    if (!failed) failed = flock(fd,LOCK_EX|LOCK_NB) ||
        pread(fd,super,sizeof(super),1024) != sizeof(super) ||
        super[56] != 0x53 || super[57] != 0xef || memcmp(super+104,uuid,16);
    if (failed) {
        if (fd >= 0) close(fd);
        dprintf(1,"PERSISTENT166_REFUSED identity_or_lock errno=%d\n",errno);
        return -1;
    }
    persistent166_fd = fd;
    /* native_loop uses O_NOFOLLOW, so use the verified fixed path and then
     * compare the configured loop's actual backing inode to the held lock. */
    if (native_loop(3,"/mnt/lab/harmony-persistent-data-165/data.ext4",8589934592ULL)) return -1;
    struct loop_info64 info = {0};
    if (ioctl(native_fds[3],LOOP_GET_STATUS64,&info) || info.lo_inode != file.st_ino ||
        info.lo_device != (unsigned long long)file.st_dev) return -1;
    dprintf(1,"PERSISTENT166_READY nvme_backed=1 capacity=8589934592 seed_copied=0 inode_verified=1 exclusive_lock=1\n");
    return 0;
}

static void persistent166_finish_worker(void *unused)
{
    (void)unused;
    if (mkdir("/native-data166",0700) && errno != EEXIST) _exit(121);
    if (mount("/dev/loop3","/native-data166","ext4",MS_NODEV|MS_NOSUID|MS_NOEXEC,"data=ordered")) _exit(122);
    int fd = open("/native-data166",O_RDONLY|O_DIRECTORY|O_CLOEXEC);
    if (fd < 0 || syncfs(fd) || close(fd) || umount("/native-data166") ||
        fsync(persistent166_fd) || syncfs(persistent166_fd)) _exit(123);
    dprintf(1,"PERSISTENT166_FLUSHED inner_syncfs=1 inner_unmounted=1 backing_fsync=1 outer_syncfs=1\n");
}

static void persistent166_finish(void)
{
    if (persistent166_fd < 0) return;
    int result = commercial_bounded010(persistent166_finish_worker,NULL,12000);
    dprintf(1,"PERSISTENT166_FINISH status=%d clean_shutdown_not_inferred=%d\n",result,result != 0);
    close(persistent166_fd);
    persistent166_fd = -1;
}
#endif
