"""Bounded original HiLog queries for the actual original RenderService PID."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-059.py')))
source = parent['source'].replace('ORIGINAL_INIT059_', 'ORIGINAL_INIT063_').replace('GRAPHICS059_', 'GRAPHICS063_')
old = '        char text[8192], path[128];'
assert source.count(old) == 1
source = source.replace(old, old + '\n        long rs_pid = 0;')
old = '                dprintf(1, "GRAPHICS063_PROCESS sample=%u pid=%ld cmd=%s\\n", sample, pid, text);'
assert source.count(old) == 1
source = source.replace(old, '''                if (strstr(text, "/system/bin/render_service") == text && pid > rs_pid)
                    rs_pid = pid;
''' + old)
old = '        if (sample == 9 || sample == 21) {'
assert source.count(old) == 1
source = source.replace(old, '''        if ((sample == 9 || sample == 13 || sample == 17) && rs_pid > 1) {
            char rs_pid_arg[32];
            snprintf(rs_pid_arg, sizeof(rs_pid_arg), "%ld", rs_pid);
            dprintf(1, "GRAPHICS063_HILOG_QUERY sample=%u pid=%ld original_tool=1\\n", sample, rs_pid);''')
assert source.count('alarm(5);') == 1
source = source.replace('alarm(5);', 'alarm(8);')
old = 'char *const args[] = {"/system/bin/hilog", "-x", NULL};'
assert source.count(old) == 1
source = source.replace(old, 'char *const args[] = {"/system/bin/hilog", "-x", "-P", rs_pid_arg, NULL};')
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-059', 'baremetal-sdk-original-init-063')
compile(payload, 'original-graphics-063-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
