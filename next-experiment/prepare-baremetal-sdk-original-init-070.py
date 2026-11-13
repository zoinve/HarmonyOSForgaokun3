"""Read bounded guest Binder state; never alter services or authentication."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-069.py')))
source = parent['source'].replace('ORIGINAL_INIT069_', 'ORIGINAL_INIT070_').replace('GRAPHICS069_', 'GRAPHICS070_')
helper = r'''
static void graphics_binder_read_070(unsigned sample, const char *name)
{
    char path[256], data[16385];
    snprintf(path, sizeof(path), "/run/graphics-binder-debug/binder/%s", name);
    int fd = open(path, O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    if (fd < 0) {
        dprintf(1, "GRAPHICS070_BINDER_READ sample=%u name=%s bytes=-1 errno=%d\n", sample, name, errno);
        return;
    }
    ssize_t n = read(fd, data, sizeof(data) - 1);
    int saved = errno;
    close(fd);
    dprintf(1, "GRAPHICS070_BINDER_READ sample=%u name=%s bytes=%ld errno=%d\n",
            sample, name, (long)n, n < 0 ? saved : 0);
    if (n > 0) { data[n] = 0; dprintf(1, "%s\n", data); }
    dprintf(1, "GRAPHICS070_BINDER_END sample=%u name=%s\n", sample, name);
}
'''
anchor = '    for (unsigned sample = 0; sample < 48; ++sample) {'
assert source.count(anchor) == 1
# Place the helper before the observer function, not inside its body.
start = source.rfind('\nstatic ', 0, source.index(anchor))
assert start >= 0
source = source[:start] + '\n' + helper + source[start:]
anchor = '        if ((sample == 9 || sample == 13 || sample == 17 || sample == 29 || sample == 41) && rs_pid > 1) {'
assert source.count(anchor) == 1
source = source.replace(anchor, r'''        if (sample == 17 || sample == 29 || sample == 41) {
            graphics_binder_read_070(sample, "transactions");
            graphics_binder_read_070(sample, "failed_transaction_log");
            long binder_pids[] = {rs_pid, composer_pid, manager_pid};
            for (unsigned i = 0; i < 3; ++i) {
                if (binder_pids[i] <= 1) continue;
                char entry[64];
                snprintf(entry, sizeof(entry), "proc/%ld", binder_pids[i]);
                graphics_binder_read_070(sample, entry);
            }
        }
''' + anchor)
anchor = '    guest_permissive_config_047();'
assert source.count(anchor) == 1
source = source.replace(anchor, r'''    directory("/run/graphics-binder-debug", 0700);
    int debug_rc = mount("debugfs", "/run/graphics-binder-debug", "debugfs",
                         MS_NOSUID | MS_NODEV | MS_NOEXEC, NULL);
    dprintf(1, "GRAPHICS070_BINDER_MOUNT rc=%d errno=%d guest_only=1\n",
            debug_rc, debug_rc ? errno : 0);
''' + anchor)
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-069', 'baremetal-sdk-original-init-070')
compile(payload, 'original-graphics-070-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
