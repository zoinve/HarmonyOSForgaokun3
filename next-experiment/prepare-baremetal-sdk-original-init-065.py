"""Expose an authentic cached log dictionary index only to the diagnostic child."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-064.py')))
source = parent['source'].replace('ORIGINAL_INIT064_', 'ORIGINAL_INIT065_').replace('GRAPHICS064_', 'GRAPHICS065_')
source = source.replace('#define _GNU_SOURCE\n', '')
source = '#define _GNU_SOURCE\n#include <sched.h>\n' + source
old = '''            if (log_child == 0) {
                alarm(8);'''
new = '''            if (log_child == 0) {
                alarm(12);
                if (unshare(CLONE_NEWNS) ||
                    mount(NULL, "/", NULL, MS_REC | MS_PRIVATE, NULL) ||
                    mount("/graphics-dict-info.json", "/log/hilog/.dict_info.json", NULL, MS_BIND, NULL) ||
                    mount(NULL, "/log/hilog/.dict_info.json", NULL,
                          MS_BIND | MS_REMOUNT | MS_RDONLY, NULL)) {
                    dprintf(1, "GRAPHICS065_HILOG_INDEX_ERROR errno=%d\\n", errno);
                    _exit(71);
                }
                dprintf(1, "GRAPHICS065_HILOG_INDEX genuine_cache=1 private_query_namespace=1 readonly=1\\n");'''
assert source.count(old) == 1
source = source.replace(old, new)
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-064', 'baremetal-sdk-original-init-065')
compile(payload, 'original-graphics-065-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
