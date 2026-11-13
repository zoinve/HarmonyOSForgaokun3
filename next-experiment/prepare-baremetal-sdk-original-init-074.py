"""Load matching real ashmem only after isolated-guest guards, before original init."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-073.py')))
source = parent['source'].replace('ORIGINAL_INIT073_', 'ORIGINAL_INIT074_').replace('GRAPHICS073_', 'GRAPHICS074_')
for header in ('#include <sys/syscall.h>', '#include <sys/sysmacros.h>'):
    if header not in source:
        source = source.replace('#include <unistd.h>', '#include <unistd.h>\n' + header)
helper = r'''
static void graphics_ashmem_074(void)
{
    int fd = open("/graphics-ashmem.ko", O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    if (fd < 0) fail("matching guest ashmem module missing");
    long rc = syscall(SYS_finit_module, fd, "", 0);
    int saved = errno;
    close(fd);
    dprintf(1, "GRAPHICS074_ASHMEM_LOAD rc=%ld errno=%d guest_only=1\n", rc, rc ? saved : 0);
    if (rc) fail("real guest ashmem module load failed");
    char text[128];
    unsigned device_major = 0, device_minor = 0;
    if (read_path("/sys/class/misc/ashmem/dev", text, sizeof(text)) <= 0 ||
        sscanf(text, "%u:%u", &device_major, &device_minor) != 2)
        fail("real kernel ashmem device identity absent");
    struct stat st;
    if (lstat("/dev/ashmem", &st) || !S_ISCHR(st.st_mode) ||
        major(st.st_rdev) != device_major || minor(st.st_rdev) != device_minor)
        fail("ashmem node must match real registered kernel device");
    dprintf(1, "GRAPHICS074_ASHMEM_DEVICE major=%u minor=%u mode=%o kernel_registered=1\n",
            device_major, device_minor, (unsigned)(st.st_mode & 07777));
}
'''
anchor = 'int main(void)'
assert source.count(anchor) == 1
source = source.replace(anchor, helper + '\n' + anchor)
anchor = '    if (mount("devtmpfs", "/dev", "devtmpfs", MS_NOSUID, "mode=0755")) fail("genuine kernel device filesystem");'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '\n    graphics_ashmem_074();')
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-073', 'baremetal-sdk-original-init-074')
compile(payload, 'original-real-ashmem-074-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
