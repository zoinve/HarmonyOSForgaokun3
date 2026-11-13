"""Read exact pinned original library state, without ptrace or target writes."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-070.py')))
source = parent['source'].replace('ORIGINAL_INIT070_', 'ORIGINAL_INIT071_').replace('GRAPHICS070_', 'GRAPHICS071_')
helper = r'''
/* Private observations for the unchanged original SDK image only. Not a public ABI.
 * librender_service.z.so sha256 fce31219aad17f8fa8a4dcd910284caa030fc0cf081e30037c8c730b5d53a633
 * libcomposer.z.so sha256 c031105598312ed0d074ccf0742f985b22c701c905cac1bb679746112c582d6d
 */
static void graphics_state_read_071(unsigned sample, long pid, const char *library,
                                    const char *field, unsigned long offset, size_t width)
{
    char path[128], line[2048], needle[128];
    unsigned long base = 0;
    snprintf(needle, sizeof(needle), "/%s", library);
    snprintf(path, sizeof(path), "/proc/%ld/maps", pid);
    FILE *maps = fopen(path, "re");
    if (maps) {
        while (fgets(line, sizeof(line), maps)) {
            unsigned long begin = 0, end = 0, file_offset = 0;
            char permissions[8];
            if (sscanf(line, "%lx-%lx %7s %lx", &begin, &end, permissions, &file_offset) != 4)
                continue;
            char *name = strstr(line, needle);
            if (name && file_offset == 0 && (name[strlen(needle)] == '\n' || name[strlen(needle)] == 0)) {
                base = begin;
                break;
            }
        }
        fclose(maps);
    }
    if (!base) {
        dprintf(1, "GRAPHICS071_STATE sample=%u pid=%ld field=%s bytes=-1 errno=%d mapped=0 private_hash_specific_state=1\n",
                sample, pid, field, ENOENT);
        return;
    }
    snprintf(path, sizeof(path), "/proc/%ld/mem", pid);
    int fd = open(path, O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    unsigned long long value = 0;
    ssize_t count = -1;
    int error = errno;
    if (fd >= 0) {
        count = pread(fd, &value, width, (off_t)(base + offset));
        error = count < 0 ? errno : 0;
        close(fd);
    }
    dprintf(1, "GRAPHICS071_STATE sample=%u pid=%ld field=%s bytes=%ld errno=%d base=0x%lx value=0x%llx private_hash_specific_state=1\n",
            sample, pid, field, (long)count, error, base, value);
}
'''
anchor = 'static void graphics_binder_read_070('
assert source.count(anchor) == 1
source = source.replace(anchor, helper + '\n' + anchor)
anchor = '            graphics_binder_read_070(sample, "transactions");'
assert source.count(anchor) == 1
source = source.replace(anchor, r'''            if (rs_pid > 1) {
                graphics_state_read_071(sample, rs_pid, "librender_service.z.so", "backend_guard", 0x83fab0, 1);
                graphics_state_read_071(sample, rs_pid, "librender_service.z.so", "backend_device", 0x83fa08, 8);
                graphics_state_read_071(sample, rs_pid, "libcomposer.z.so", "device_guard", 0x14100, 1);
                graphics_state_read_071(sample, rs_pid, "libcomposer.z.so", "composer_remote", 0x14138, 8);
            }
''' + anchor)
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-070', 'baremetal-sdk-original-init-071')
compile(payload, 'original-state-071-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
