"""Fresh full original-init graph observation with guest-only permissive mode."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-038.py')))['payload']
for old, new in [('original-init-qemu-038', 'original-init-qemu-047'),
                 ('original-init-038', 'original-init-047'),
                 ('harmony-sdk-qemu038-', 'harmony-sdk-qemu047-'),
                 ('ORIGINAL_INIT038_', 'ORIGINAL_INIT047_'),
                 ('enforcing=1', 'enforcing=0'),
                 ('timeout=60)', 'timeout=90)'),
                 ('timeout_seconds=60', 'timeout_seconds=90')]:
    assert old in payload, old
    payload = payload.replace(old, new)
anchor = "  report['helper_failure_observed']=b'ORIGINAL_INIT047_FAIL' in data"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, anchor + """
  report['permissive_guest_config_observed']=b'GRAPHICS047_CONFIG guest_only=1 mode=permissive' in data
  report['graphics_process_snapshot_observed']=b'GRAPHICS047_PROCESS' in data
  report['full_graph_observation_only']=True
  report['desktop_verified']=False
""")
compile(payload, 'original-graphics-047-run', 'exec')
if __name__ == '__main__':
    result = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=payload, text=True, timeout=420)
    raise SystemExit(result.returncode)
