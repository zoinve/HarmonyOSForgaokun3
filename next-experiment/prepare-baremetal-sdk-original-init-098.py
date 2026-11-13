"""Read genuine power-manager decisions; change no timeout, input or authentication."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-097.py')))
source = parent['source'].replace('ORIGINAL_INIT097_', 'ORIGINAL_INIT098_').replace('GRAPHICS097_', 'GRAPHICS098_')
start = source.index('static void graphics_render_service_query_097(')
end = source.index('\nstatic void ', start + 1)
helper = source[start:end].replace('graphics_render_service_query_097', 'graphics_power_service_query_098')
helper = helper.replace('rs_pid', 'powermgr_pid').replace('RS_QUERY', 'POWER_SERVICE_QUERY')
source = source[:end] + '\n' + helper + source[end:]
anchor = '        long sceneboard_pid = 0;'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '\n        long powermgr_pid = 0;')
anchor = '                    sceneboard_pid = pid;'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '''
                if ((!strncmp(text, "powermgr ", sizeof("powermgr ") - 1) ||
                     !strncmp(text, "/system/bin/powermgr ", sizeof("/system/bin/powermgr ") - 1)) && pid > powermgr_pid)
                    powermgr_pid = pid;''')
anchor = '        if ((sample == 41 || sample == 49 || sample == 61) && rs_pid > 1)'
assert source.count(anchor) == 1
source = source.replace(anchor, '''        if ((sample == 41 || sample == 49 || sample == 61) && powermgr_pid > 1)
            graphics_power_service_query_098(sample, powermgr_pid);
''' + anchor)
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-097', 'baremetal-sdk-original-init-098')
compile(payload, 'original-power-service-098-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
