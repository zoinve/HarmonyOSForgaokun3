"""Query real Foundation tail logs after the same normal original-tool requests."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-077.py')))
source = parent['source'].replace('ORIGINAL_INIT077_', 'ORIGINAL_INIT078_').replace('GRAPHICS077_', 'GRAPHICS078_')
helper = r'''
static void graphics_foundation_query_078(unsigned sample, long foundation_pid)
{
    dprintf(1, "GRAPHICS078_FOUNDATION_QUERY sample=%u pid=%ld original_tool=1 tail=200\n", sample, foundation_pid);
    pid_t child = fork();
    if (child == 0) {
        alarm(12);
        char argument[32];
        snprintf(argument, sizeof(argument), "%ld", foundation_pid);
        char *const args[] = {"/system/bin/hilog", "-x", "-z", "200", "-P", argument, NULL};
        execv(args[0], args);
        dprintf(1, "GRAPHICS078_FOUNDATION_QUERY_EXEC_ERROR errno=%d\n", errno);
        _exit(74);
    }
    int status = -1;
    if (child > 0) {
        while (waitpid(child, &status, 0) < 0 && errno == EINTR) {}
    }
    dprintf(1, "GRAPHICS078_FOUNDATION_QUERY_END sample=%u pid=%ld status=%d\n", sample, foundation_pid, status);
}
'''
anchor = 'static void graphics_desktop_tool_077('
assert source.count(anchor) == 1
source = source.replace(anchor, helper + '\n' + anchor)
anchor = '        long rs_pid = 0;'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '\n        long foundation_pid = 0;')
anchor = '                dprintf(1, "GRAPHICS078_PROCESS sample=%u pid=%ld cmd=%s\\n", sample, pid, text);'
assert source.count(anchor) == 1
source = source.replace(anchor, '''                if ((strstr(text, "/system/bin/foundation ") == text || !strncmp(text, "foundation ", 11)) && pid > foundation_pid)
                    foundation_pid = pid;
''' + anchor)
anchor = '        graphics_trace_capture_055(sample);'
assert source.count(anchor) == 1
source = source.replace(anchor, '''        if ((sample == 24 || sample == 30 || sample == 41) && foundation_pid > 1)
            graphics_foundation_query_078(sample, foundation_pid);
''' + anchor)
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-077', 'baremetal-sdk-original-init-078')
compile(payload, 'original-desktop-errors-078-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
