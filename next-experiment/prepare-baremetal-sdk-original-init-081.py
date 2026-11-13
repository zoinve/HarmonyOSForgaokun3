"""Observe original SAMGR profile loading; never inject profiles or userdata."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-080.py')))
source = parent['source'].replace('ORIGINAL_INIT080_', 'ORIGINAL_INIT081_').replace('GRAPHICS080_', 'GRAPHICS081_')
start = source.index('static void graphics_foundation_query_078(')
end = source.index('\nstatic ', start + 1)
query = source[start:end].replace('graphics_foundation_query_078', 'graphics_samgr_query_081')
query = query.replace('foundation_pid', 'samgr_pid').replace('FOUNDATION_QUERY', 'SAMGR_QUERY').replace('tail=200', 'head=600')
profiles = r'''
static void graphics_samgr_profiles_081(unsigned sample, long pid)
{
    const char *roots[] = {"system", "vendor", "sys_prod"};
    for (unsigned i = 0; i < sizeof(roots) / sizeof(roots[0]); ++i) {
        char path[256], body[1024];
        snprintf(path, sizeof(path), "/proc/%ld/root/%s/profile/installs.json", pid, roots[i]);
        int fd = open(path, O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
        ssize_t n = fd < 0 ? -1 : read(fd, body, sizeof(body));
        int error = n < 0 ? errno : 0;
        if (fd >= 0) close(fd);
        dprintf(1, "GRAPHICS081_SAMGR_PROFILE sample=%u pid=%ld root=%s bytes=%ld errno=%d\n",
                sample, pid, roots[i], (long)n, error);
        if (n > 0) (void)write(1, body, (size_t)n);
        dprintf(1, "\nGRAPHICS081_SAMGR_PROFILE_END\n");
    }
}
'''
source = source[:start] + profiles + query + '\n' + source[start:]
old = 'long foundation_pid = 0;'
assert source.count(old) == 1
source = source.replace(old, old + '\n        long samgr_pid = 0;')
old = '                if ((strstr(text, "/system/bin/foundation ")'
assert source.count(old) == 1
source = source.replace(old, '''                if ((strstr(text, "/system/bin/samgr ") == text || !strncmp(text, "samgr ", 6)) && pid > samgr_pid)
                    samgr_pid = pid;
''' + old)
old = '        graphics_trace_capture_055(sample);'
assert source.count(old) == 1
source = source.replace(old, '''        if ((sample == 17 || sample == 29) && samgr_pid > 1) {
            graphics_samgr_profiles_081(sample, samgr_pid);
            graphics_samgr_query_081(sample, samgr_pid);
        }
''' + old)
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-080', 'baremetal-sdk-original-init-081')
compile(payload, 'original-samgr-profile-081-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
