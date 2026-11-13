"""Capture bounded real bridge results in the volatile original-service guest."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-054.py')))
source = parent['source'].replace('ORIGINAL_INIT054_', 'ORIGINAL_INIT055_').replace('GRAPHICS054_', 'GRAPHICS055_')
anchor = 'static void graphics_observer_047(void)'
assert source.count(anchor) == 1
source = source.replace(anchor, r'''
static void graphics_trace_capture_055(unsigned sample)
{
    DIR *dir = opendir("/run/graphics-trace");
    if (!dir) return;
    struct dirent *entry;
    unsigned files = 0;
    while ((entry = readdir(dir)) && files < 32) {
        if (strncmp(entry->d_name, "egl-", 4) || strchr(entry->d_name, '/')) continue;
        char path[320], data[32769];
        snprintf(path, sizeof(path), "/run/graphics-trace/%s", entry->d_name);
        int fd = open(path, O_RDONLY | O_NOFOLLOW | O_CLOEXEC | O_NONBLOCK);
        if (fd < 0) continue;
        struct stat st;
        if (!fstat(fd, &st) && S_ISREG(st.st_mode) && st.st_size <= 32768 && st.st_nlink == 1) {
            ssize_t n = read(fd, data, sizeof(data) - 1);
            if (n > 0) {
                data[n] = 0;
                dprintf(1, "GRAPHICS055_TRACE sample=%u file=%s uid=%u bytes=%zd\n%s",
                        sample, entry->d_name, (unsigned)st.st_uid, n, data);
            }
            ++files;
        }
        close(fd);
    }
    closedir(dir);
}

''' + anchor)
anchor = '        sleep(5);'
assert source.count(anchor) == 1
source = source.replace(anchor, '        graphics_trace_capture_055(sample);\n' + anchor)
anchor = '    graphics_egl_054();'
assert source.count(anchor) == 1
source = source.replace(anchor, '''    directory("/run/graphics-trace", 01777);
    if (chmod("/run/graphics-trace", 01777)) fail("RAM trace directory permissions");
''' + anchor)
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-054', 'baremetal-sdk-original-init-055')
compile(payload, 'original-graphics-055-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
