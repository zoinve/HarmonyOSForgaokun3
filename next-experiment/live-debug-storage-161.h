#ifndef LIVE_DEBUG_STORAGE_161_H
#define LIVE_DEBUG_STORAGE_161_H
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <sys/statvfs.h>
#include <unistd.h>

/* Fixed stage numbers only: never report key bytes, raw logs or caller text. */
static int live_storage161_refuse(unsigned item, unsigned stage, int error)
{
    if (!error) error = EIO;
    dprintf(1,"LIVE161_STORAGE_REFUSED item=%u stage=%u errno=%d\n",item,stage,error);
    errno = error;
    return -1;
}

static int live_storage161_bind(int fd, const char *destination, unsigned item)
{
    struct stat source, target;
    if (fstat(fd,&source)) return live_storage161_refuse(item,1,errno);
    if (!S_ISREG(source.st_mode)) return live_storage161_refuse(item,2,EINVAL);
    if (lstat(destination,&target)) return live_storage161_refuse(item,3,errno);
    if (!S_ISREG(target.st_mode) || target.st_size) return live_storage161_refuse(item,4,EINVAL);
    char path[64];
    snprintf(path,sizeof(path),"/proc/self/fd/%d",fd);
    if (mount(path,destination,NULL,MS_BIND,NULL)) return live_storage161_refuse(item,5,errno);
    if (mount(NULL,destination,NULL,MS_REMOUNT | MS_BIND | MS_RDONLY | MS_NOSUID | MS_NODEV | MS_NOEXEC,NULL))
        return live_storage161_refuse(item,6,errno);
    struct statvfs flags;
    if (statvfs(destination,&flags)) return live_storage161_refuse(item,7,errno);
    if (!(flags.f_flag & ST_RDONLY)) return live_storage161_refuse(item,8,EROFS);
    dprintf(1,"LIVE161_STORAGE_READY item=%u readonly=1 source_regular=1\n",item);
    return 0;
}

static int live_storage161_key(const char *source, const char *destination)
{
    int fd = open(source,O_RDONLY | O_NOFOLLOW | O_CLOEXEC);
    if (fd < 0) return live_storage161_refuse(3,9,errno);
    struct stat metadata;
    if (fstat(fd,&metadata)) {
        int error = errno; close(fd); return live_storage161_refuse(3,10,error);
    }
    if (!S_ISREG(metadata.st_mode) || metadata.st_uid || (metadata.st_mode & 0077) ||
        metadata.st_size < 100 || metadata.st_size > 4096) {
        close(fd); return live_storage161_refuse(3,11,EINVAL);
    }
    int out = open(destination,O_WRONLY | O_CREAT | O_EXCL | O_NOFOLLOW | O_CLOEXEC,0600);
    if (out < 0) { int error = errno; close(fd); return live_storage161_refuse(3,12,error); }
    char data[4096];
    ssize_t count;
    do { count = pread(fd,data,(size_t)metadata.st_size,0); } while (count < 0 && errno == EINTR);
    int error = count < 0 ? errno : EIO;
    if (count != metadata.st_size) {
        explicit_bzero(data,sizeof(data)); close(out); close(fd);
        return live_storage161_refuse(3,13,error);
    }
    size_t written = 0;
    while (written < (size_t)count) {
        ssize_t n = write(out,data + written,(size_t)count - written);
        if (n < 0 && errno == EINTR) continue;
        if (n <= 0) {
            error = n < 0 ? errno : EIO;
            explicit_bzero(data,sizeof(data)); close(out); close(fd);
            return live_storage161_refuse(3,14,error);
        }
        written += (size_t)n;
    }
    explicit_bzero(data,sizeof(data));
    close(fd);
    if (close(out)) return live_storage161_refuse(3,15,errno);
    dprintf(1,"LIVE161_STORAGE_READY item=3 key_copied_in_ram=1 key_material_not_reported=1\n");
    return 0;
}
#endif
