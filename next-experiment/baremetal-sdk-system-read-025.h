/* QEMU-only read-only original image check. No executable or image is modified. */
#include <linux/fs.h>
#include <sys/statvfs.h>
#include <time.h>

static void mount_original_system_025(void)
{
    char number[64];
    int ready = 0;
    for (unsigned i = 0; i < 100; ++i) {
        if (text("/sys/class/block/vda/dev", number, sizeof(number)) > 0) {
            ready = 1;
            break;
        }
        struct timespec interval = {0, 20000000};
        nanosleep(&interval, NULL);
    }
    require(ready, "bounded discovery of explicit QEMU read-only image device");
    unsigned major_number, minor_number;
    require(sscanf(number, "%u:%u", &major_number, &minor_number) == 2, "actual image block identity");
    require(!mknod("/dev/sdk-system", S_IFBLK | 0400, makedev(major_number, minor_number)), "RAM-only read-only image node");
    int fd = open("/dev/sdk-system", O_RDONLY | O_CLOEXEC), read_only = 0;
    require(fd >= 0 && !ioctl(fd, BLKROGET, &read_only) && read_only == 1,
            "QEMU must expose original image as physically read-only block device");
    close(fd);
    require(!mkdir("/sdk-system", 0755), "private image mount point");
    require(!mount("/dev/sdk-system", "/sdk-system", "ext4",
                   MS_RDONLY | MS_NODEV | MS_NOSUID | MS_NOEXEC, "noload"),
            "mount original ext4 read-only without journal replay or execution");
    struct statvfs flags;
    require(!statvfs("/sdk-system", &flags) && (flags.f_flag & ST_RDONLY) && (flags.f_flag & ST_NOEXEC),
            "actual read-only noexec filesystem flags");
}

static void inspect_original_system_025(void)
{
    const char *path = "/sdk-system/system/bin/samgr";
    char context[128] = {0};
    require(getxattr(path, "security.selinux", context, sizeof(context)-1) > 0 &&
            !strcmp(context, "u:object_r:samain_exec:s0"), "original samgr xattr under enforcing policy");
    int fd = open(path, O_RDONLY | O_CLOEXEC);
    unsigned char magic[4];
    require(fd >= 0 && read(fd, magic, sizeof(magic)) == sizeof(magic) &&
            !memcmp(magic, "\177ELF", sizeof(magic)), "read original executable under production init policy");
    close(fd);
    dprintf(1, "SELINUX025_STORAGE_PASS readonly_block=1 readonly_noexec_noload_mount=1 "
               "original_samgr_label=1 original_elf_read=1 services_not_tested=1\n");
}
