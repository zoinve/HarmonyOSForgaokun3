"""Observe authentic composer/HDF-manager logs without changing service behavior."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-067.py')))
source = parent['source'].replace('ORIGINAL_INIT067_', 'ORIGINAL_INIT068_').replace('GRAPHICS067_', 'GRAPHICS068_')
anchor = 'long rs_pid = 0;'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '\n        long composer_pid = 0, manager_pid = 0;')
anchor = '                dprintf(1, "GRAPHICS068_PROCESS sample=%u pid=%ld cmd=%s\\n", sample, pid, text);'
assert source.count(anchor) == 1
source = source.replace(anchor, '''                if ((!strncmp(text, "composer_host ", 14) ||
                     (strstr(text, "/vendor/bin/hdf_devhost") == text && strstr(text, "-n composer_host"))) && pid > composer_pid)
                    composer_pid = pid;
                if (strstr(text, "/system/bin/hdf_devmgr") == text && pid > manager_pid)
                    manager_pid = pid;
''' + anchor)
anchor = '        graphics_trace_capture_055(sample);'
assert source.count(anchor) == 1
source = source.replace(anchor, '''        if (sample == 17 || sample == 29 || sample == 41) {
            long query_pids[] = {rs_pid, composer_pid, manager_pid};
            for (unsigned target = 1; target < 3; ++target) {
                if (query_pids[target] <= 1) continue;
                char query_pid_arg[32];
                snprintf(query_pid_arg, sizeof(query_pid_arg), "%ld", query_pids[target]);
                dprintf(1, "GRAPHICS068_HDF_HILOG_QUERY sample=%u pid=%ld target=%u original_tool=1\\n",
                        sample, query_pids[target], target);
                pid_t child = fork();
                if (child == 0) {
                    alarm(8);
                    char *const args[] = {"/system/bin/hilog", "-x", "-P", query_pid_arg, NULL};
                    execv(args[0], args);
                    dprintf(1, "GRAPHICS068_HDF_HILOG_EXEC_ERROR errno=%d\\n", errno);
                    _exit(127);
                }
                if (child > 0) {
                    int status = 0;
                    if (waitpid(child, &status, 0) == child)
                        dprintf(1, "GRAPHICS068_HDF_HILOG_EXIT pid=%ld status=%d\\n", query_pids[target], status);
                }
            }
        }
''' + anchor)
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-067', 'baremetal-sdk-original-init-068')
compile(payload, 'original-graphics-068-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
