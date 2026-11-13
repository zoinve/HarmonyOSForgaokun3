"""Read each original render process and bounded task state; no attach or writes."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-071.py')))
source = parent['source'].replace('ORIGINAL_INIT071_', 'ORIGINAL_INIT072_').replace('GRAPHICS071_', 'GRAPHICS072_')
helper = r'''
static void graphics_role_read_072(unsigned sample, long pid)
{
    char path[256], line[512];
    snprintf(path, sizeof(path), "/proc/%ld/status", pid);
    FILE *status = fopen(path, "re");
    if (status) {
        while (fgets(line, sizeof(line), status)) {
            if (!strncmp(line, "PPid:", 5)) {
                dprintf(1, "GRAPHICS072_ROLE sample=%u pid=%ld %s", sample, pid, line);
                break;
            }
        }
        fclose(status);
    }
    graphics_state_read_071(sample, pid, "librender_service.z.so", "backend_guard", 0x83fab0, 1);
    graphics_state_read_071(sample, pid, "librender_service.z.so", "backend_device", 0x83fa08, 8);
    graphics_state_read_071(sample, pid, "libcomposer.z.so", "device_guard", 0x14100, 1);
    graphics_state_read_071(sample, pid, "libcomposer.z.so", "composer_remote", 0x14138, 8);
    snprintf(path, sizeof(path), "/proc/%ld/task", pid);
    DIR *tasks = opendir(path);
    if (!tasks) return;
    struct dirent *entry;
    unsigned tid_count = 0;
    while (tid_count < 16 && (entry = readdir(tasks))) {
        char *end = NULL;
        long tid = strtol(entry->d_name, &end, 10);
        if (!*entry->d_name || *end || tid <= 0) continue;
        ++tid_count;
        const char *kinds[] = {"wchan", "syscall"};
        for (unsigned k = 0; k < 2; ++k) {
            snprintf(path, sizeof(path), "/proc/%ld/task/%ld/%s", pid, tid, kinds[k]);
            int fd = open(path, O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
            ssize_t count = fd < 0 ? -1 : read(fd, line, sizeof(line) - 1);
            int error = count < 0 ? errno : 0;
            if (fd >= 0) close(fd);
            if (count > 0) {
                while (count > 0 && (line[count - 1] == '\n' || line[count - 1] == '\r')) --count;
                line[count] = 0;
            }
            dprintf(1, "GRAPHICS072_THREAD sample=%u pid=%ld tid=%ld kind=%s bytes=%ld errno=%d data=%s\n",
                    sample, pid, tid, kinds[k], (long)count, error, count > 0 ? line : "<none>");
        }
    }
    closedir(tasks);
}
'''
anchor = 'static void graphics_binder_read_070('
assert source.count(anchor) == 1
source = source.replace(anchor, helper + '\n' + anchor)
start = source.index('            if (rs_pid > 1) {\n                graphics_state_read_071(')
end = source.index('            graphics_binder_read_070(sample, "transactions");', start)
source = source[:start] + source[end:]
anchor = '                dprintf(1, "GRAPHICS072_PROCESS sample=%u pid=%ld cmd=%s\\n", sample, pid, text);'
assert source.count(anchor) == 1
source = source.replace(anchor, '''                if ((sample == 17 || sample == 29 || sample == 41) &&
                    strstr(text, "/system/bin/render_service") == text)
                    graphics_role_read_072(sample, pid);
''' + anchor)
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-071', 'baremetal-sdk-original-init-072')
compile(payload, 'original-roles-072-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
