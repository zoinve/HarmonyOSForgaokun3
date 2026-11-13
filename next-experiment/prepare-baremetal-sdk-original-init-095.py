"""Query genuine SceneBoard logs after original AppSpawn, changing no checks."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-094.py')))
source = parent['source'].replace('ORIGINAL_INIT094_', 'ORIGINAL_INIT095_').replace('GRAPHICS094_', 'GRAPHICS095_')
start = source.index('static void graphics_foundation_query_078(')
end = source.index('\nstatic void ', start + 1)
helper = source[start:end].replace('graphics_foundation_query_078', 'graphics_sceneboard_query_095')
helper = helper.replace('foundation_pid', 'sceneboard_pid').replace('FOUNDATION_QUERY', 'SCENEBOARD_QUERY')
assert helper.count('"-z", "200", "-P"') == 1
helper = helper.replace('"-z", "200", "-P"', '"-z", "400", "-P"').replace('tail=200', 'tail=400')
source = source[:end] + '\n' + helper + source[end:]
anchor = '        long appspawn_pid = 0;'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '\n        long sceneboard_pid = 0;')
anchor = '                    appspawn_pid = pid;'
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '''
                if (!strncmp(text, "com.ohos.sceneboard ", sizeof("com.ohos.sceneboard ") - 1) && pid > sceneboard_pid)
                    sceneboard_pid = pid;''')
anchor = '!strstr(text, "appspawn")) continue;'
assert source.count(anchor) == 1
source = source.replace(anchor, '!strstr(text, "appspawn") && !strstr(text, "com.ohos.sceneboard")) continue;')
anchor = '''        if ((sample == 41 || sample == 49 || sample == 61) && appspawn_pid > 1) {
            graphics_appspawn_query_093(sample, appspawn_pid, 0);
            graphics_appspawn_query_093(sample, appspawn_pid, 1);
        }'''
assert source.count(anchor) == 1
source = source.replace(anchor, anchor + '''
        if ((sample == 41 || sample == 49 || sample == 61) && sceneboard_pid > 1)
            graphics_sceneboard_query_095(sample, sceneboard_pid);''')
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-094', 'baremetal-sdk-original-init-095')
compile(payload, 'original-sceneboard-logs-095-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
