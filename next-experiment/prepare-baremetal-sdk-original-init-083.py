"""Separate bootstrap caller queries the original public config API, not SAMGR."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-082.py')))
source = parent['source'].replace('ORIGINAL_INIT082_', 'ORIGINAL_INIT083_').replace('GRAPHICS082_', 'GRAPHICS083_')
anchor = '            graphics_config_parameters_082(sample);'
assert source.count(anchor) == 1
source = source.replace(anchor, r'''            dprintf(1, "GRAPHICS083_CONFIG_QUERY sample=%u diagnostic_caller_not_samgr=1\n", sample);
            pid_t query_child = fork();
            if (query_child == 0) {
                alarm(10);
                char *const args[] = {"/graphics-config-query", NULL};
                execv(args[0], args);
                dprintf(1, "GRAPHICS083_CONFIG_QUERY_EXEC_ERROR errno=%d\n", errno);
                _exit(73);
            }
            int query_status = -1;
            if (query_child > 0) while (waitpid(query_child, &query_status, 0) < 0 && errno == EINTR) {}
            dprintf(1, "GRAPHICS083_CONFIG_QUERY_END sample=%u status=%d\n", sample, query_status);
''' + anchor)
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-082', 'baremetal-sdk-original-init-083')
compile(payload, 'original-config-query-083-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180).returncode)
