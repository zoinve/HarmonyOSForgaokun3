"""Observe actual process population without starting or reidentifying services."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-074.py')))
source = parent['source'].replace('ORIGINAL_INIT074_', 'ORIGINAL_INIT076_').replace('GRAPHICS074_', 'GRAPHICS076_')
helper = r'''
static void graphics_all_process_076(unsigned sample, long pid, const char *cmd)
{
    char path[128], data[4096];
    dprintf(1, "GRAPHICS076_ALL_PROCESS sample=%u pid=%ld cmd=%s\n", sample, pid, cmd);
    snprintf(path, sizeof(path), "/proc/%ld/status", pid);
    if (read_path(path, data, sizeof(data)) > 0) {
        char *uid = strstr(data, "Uid:");
        if (uid) {
            char *end = strchr(uid, '\n');
            if (end) *end = 0;
            dprintf(1, "GRAPHICS076_ALL_IDENTITY sample=%u pid=%ld %s\n", sample, pid, uid);
        }
    }
    snprintf(path, sizeof(path), "/proc/%ld/attr/current", pid);
    ssize_t size = read_path(path, data, sizeof(data));
    if (size > 0) {
        while (size > 0 && (data[size - 1] == '\n' || data[size - 1] == '\r')) --size;
        data[size] = 0;
        dprintf(1, "GRAPHICS076_ALL_DOMAIN sample=%u pid=%ld value=%s\n", sample, pid, data);
    }
}
'''
anchor = 'static void graphics_role_read_072('
assert source.count(anchor) == 1
source = source.replace(anchor, helper + '\n' + anchor)
anchor = '        DIR *processes = opendir("/proc");'
assert source.count(anchor) == 1
source = source.replace(anchor, '        unsigned all_process_count = 0;\n' + anchor)
anchor = "                for (ssize_t i = 0; i < n; ++i) if (!text[i]) text[i] = ' ';"
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '''
                if ((sample == 17 || sample == 29 || sample == 41) && all_process_count++ < 256)
                    graphics_all_process_076(sample, pid, text);''')
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-074', 'baremetal-sdk-original-init-076')
compile(payload, 'original-content-076-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
