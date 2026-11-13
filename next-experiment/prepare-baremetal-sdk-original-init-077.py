"""Request original bundle metadata and normal SceneBoard start; never bypass checks."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-076.py')))
source = parent['source'].replace('ORIGINAL_INIT076_', 'ORIGINAL_INIT077_').replace('GRAPHICS076_', 'GRAPHICS077_')
helper = r'''
static void graphics_desktop_tool_077(unsigned sample, unsigned operation)
{
    dprintf(1, "GRAPHICS077_DESKTOP_TOOL sample=%u operation=%u original_binary=1 normal_authorization=1\n",
            sample, operation);
    pid_t child = fork();
    if (child == 0) {
        alarm(20);
        char *const query[] = {"/system/bin/bm", "dump", "-n", "com.ohos.sceneboard", NULL};
        char *const start[] = {"/system/bin/aa", "start", "-b", "com.ohos.sceneboard",
            "-a", "com.ohos.sceneboard.MainAbility", "-m", "pc_sceneboard", NULL};
        char *const *args = operation == 1 ? query : start;
        execv(args[0], args);
        dprintf(1, "GRAPHICS077_DESKTOP_TOOL_EXEC_ERROR errno=%d\n", errno);
        _exit(73);
    }
    int status = -1;
    if (child > 0) {
        while (waitpid(child, &status, 0) < 0 && errno == EINTR) {}
    }
    dprintf(1, "GRAPHICS077_DESKTOP_TOOL_END sample=%u operation=%u pid=%ld status=%d\n",
            sample, operation, (long)child, status);
}
'''
anchor = 'static void graphics_all_process_076('
assert source.count(anchor) == 1
source = source.replace(anchor, helper + '\n' + anchor)
anchor = '        long rs_pid = 0;'
assert source.count(anchor) == 1
source = source.replace(anchor, '''        if (sample == 23) graphics_desktop_tool_077(sample, 1);
        if (sample == 29) graphics_desktop_tool_077(sample, 2);
''' + anchor)
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-076', 'baremetal-sdk-original-init-077')
compile(payload, 'original-desktop-077-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
