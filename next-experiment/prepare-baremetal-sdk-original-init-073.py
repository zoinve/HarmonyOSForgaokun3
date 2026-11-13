"""Increase passive task coverage and record real thread names; no service changes."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-072.py')))
source = parent['source'].replace('ORIGINAL_INIT072_', 'ORIGINAL_INIT073_').replace('GRAPHICS072_', 'GRAPHICS073_')
for old, new in [('tid_count < 16', 'tid_count < 128'),
                 ('const char *kinds[] = {"wchan", "syscall"};',
                  'const char *kinds[] = {"comm", "wchan", "syscall"};'),
                 ('for (unsigned k = 0; k < 2; ++k)',
                  'for (unsigned k = 0; k < sizeof(kinds) / sizeof(kinds[0]); ++k)')]:
    # The DRM-node loop also uses k<2. Restrict this edit to the task helper.
    start = source.index('static void graphics_role_read_072(')
    end = source.index('static void graphics_binder_read_070(', start)
    helper = source[start:end]
    assert helper.count(old) == 1, old
    source = source[:start] + helper.replace(old, new) + source[end:]
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-072', 'baremetal-sdk-original-init-073')
compile(payload, 'original-workers-073-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
