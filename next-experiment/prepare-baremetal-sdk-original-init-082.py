"""Observe original configuration parameter values without changing policy/profiles."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-081.py')))
source = parent['source'].replace('ORIGINAL_INIT081_', 'ORIGINAL_INIT082_').replace('GRAPHICS081_', 'GRAPHICS082_')
helper = r'''
static void graphics_config_parameters_082(unsigned sample)
{
    const char *keys[] = {"const.cust.config_dir_layer", "const.cust.follow_x_rules"};
    for (unsigned i = 0; i < sizeof(keys) / sizeof(keys[0]); ++i) {
        dprintf(1, "GRAPHICS082_CONFIG_PARAM sample=%u key=%s original_tool=1 read_only=1\n", sample, keys[i]);
        pid_t child = fork();
        if (child == 0) {
            alarm(8);
            char *const args[] = {"/system/bin/param", "get", (char *)keys[i], NULL};
            execv(args[0], args);
            dprintf(1, "GRAPHICS082_CONFIG_PARAM_EXEC_ERROR errno=%d\n", errno);
            _exit(73);
        }
        int status = -1;
        if (child > 0) while (waitpid(child, &status, 0) < 0 && errno == EINTR) {}
        dprintf(1, "GRAPHICS082_CONFIG_PARAM_END sample=%u key=%s status=%d\n", sample, keys[i], status);
    }
}
'''
anchor = 'static void graphics_samgr_profiles_081('
assert source.count(anchor) == 1
source = source.replace(anchor, helper + '\n' + anchor)
anchor = '            graphics_samgr_profiles_081(sample, samgr_pid);'
assert source.count(anchor) == 1
source = source.replace(anchor, '            graphics_config_parameters_082(sample);\n' + anchor)
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-081', 'baremetal-sdk-original-init-082')
compile(payload, 'original-config-policy-082-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
