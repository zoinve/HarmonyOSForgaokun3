"""Retain genuine SceneBoard queries without repeated application maps dumps."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-095.py')))
source = parent['source'].replace('ORIGINAL_INIT095_', 'ORIGINAL_INIT096_').replace('GRAPHICS095_', 'GRAPHICS096_')
discovery = '''                if (!strncmp(text, "com.ohos.sceneboard ", sizeof("com.ohos.sceneboard ") - 1) && pid > sceneboard_pid)
                    sceneboard_pid = pid;'''
assert source.count(discovery) == 1
source = source.replace(discovery, '')
anchor = '                if (!strstr(text, "render_service")'
assert source.count(anchor) == 1
source = source.replace(anchor, discovery + '\n' + anchor)
anchor = '!strstr(text, "appspawn") && !strstr(text, "com.ohos.sceneboard")) continue;'
assert source.count(anchor) == 1
source = source.replace(anchor, '!strstr(text, "appspawn")) continue;')
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-095', 'baremetal-sdk-original-init-096')
compile(payload, 'original-sceneboard-late-096-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
