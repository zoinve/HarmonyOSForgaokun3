"""Read original RenderService logs and power parameters; override no protections."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-096.py')))
source = parent['source'].replace('ORIGINAL_INIT096_', 'ORIGINAL_INIT097_').replace('GRAPHICS096_', 'GRAPHICS097_')
start = source.index('static void graphics_sceneboard_query_095(')
end = source.index('\nstatic void ', start + 1)
helper = source[start:end].replace('graphics_sceneboard_query_095', 'graphics_render_service_query_097')
helper = helper.replace('sceneboard_pid', 'rs_pid').replace('SCENEBOARD_QUERY', 'RS_QUERY')
power_helper = r'''
static void graphics_power_query_097(unsigned sample)
{
    const char *keys[] = {"startup.device.ctl", "ohos.startup.powerctrl"};
    for (unsigned k = 0; k < 2; ++k) {
        dprintf(1, "GRAPHICS097_POWER_QUERY sample=%u key=%s original_tool=1 read_only=1\n", sample, keys[k]);
        pid_t child = fork();
        if (child == 0) {
            alarm(5);
            char *const args[] = {"/system/bin/param", "get", (char *)keys[k], NULL};
            execv(args[0], args);
            dprintf(1, "GRAPHICS097_POWER_QUERY_EXEC_ERROR errno=%d\n", errno);
            _exit(74);
        }
        int status = -1;
        if (child > 0) {
            while (waitpid(child, &status, 0) < 0 && errno == EINTR) {}
        }
        dprintf(1, "GRAPHICS097_POWER_QUERY_END sample=%u key=%s status=%d\n", sample, keys[k], status);
    }
}
'''
source = source[:end] + '\n' + helper + '\n' + power_helper + source[end:]
anchor = '    for (unsigned sample = 0; sample < 72; ++sample) {'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '''
        if (sample == 41 || sample == 49 || sample == 61 || sample == 69 || sample == 71)
            graphics_power_query_097(sample);''')
anchor = '        if ((sample == 41 || sample == 49 || sample == 61) && sceneboard_pid > 1)'
assert source.count(anchor) == 1
source = source.replace(anchor, '''        if ((sample == 41 || sample == 49 || sample == 61) && rs_pid > 1)
            graphics_render_service_query_097(sample, rs_pid);
''' + anchor)
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-096', 'baremetal-sdk-original-init-097')
compile(payload, 'original-rs-diagnostics-097-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
