"""Observe genuine later desktop requests; retain all original checks and data flow."""
from pathlib import Path
import runpy
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-091.py')))
source = parent['source'].replace('ORIGINAL_INIT091_', 'ORIGINAL_INIT092_').replace('GRAPHICS091_', 'GRAPHICS092_')
changes = [
    ('sample < 48', 'sample < 72'),
    ('if (sample == 23) graphics_desktop_tool_077(sample, 1);', 'if (sample == 45) graphics_desktop_tool_077(sample, 1);'),
    ('if (sample == 29) graphics_desktop_tool_077(sample, 2);', 'if (sample == 49) graphics_desktop_tool_077(sample, 2);'),
]
for old, new in changes:
    assert source.count(old) == 1, old
    source = source.replace(old, new)
assert source.count('sample == 41') == 8
source = source.replace('sample == 41', 'sample == 41 || sample == 49 || sample == 61')
payload = 'source=' + repr(source) + '\n' + parent['payload'][parent['payload'].index('\nfrom pathlib import Path') + 1:]
payload = payload.replace('baremetal-sdk-original-init-091', 'baremetal-sdk-original-init-092')
compile(payload, 'original-desktop-late-092-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
