"""Read-only SDK init-job inventory for the real BMS ENOENT failure."""
import subprocess

payload = r'''
from pathlib import Path
import hashlib, json, subprocess

root = Path('/home/zoinve/harmony-virgl-883/original-userdata-jobs-001')
report = Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/original-userdata-jobs-001')
root.mkdir(exist_ok=False)
report.mkdir(exist_ok=False)
images = [Path('/mnt/d/Download/pc_all_arm/system.img'), Path('/mnt/d/Download/pc_all_arm/vendor.img')]
def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b''): h.update(block)
    return h.hexdigest()
before = {str(p): digest(p) for p in images}
commands = []
for name, image, source in [('system-init', images[0], '/system/etc/init'), ('vendor-init', images[1], '/etc/init')]:
    target = root / name
    target.mkdir()
    command = ['debugfs', '-R', 'rdump ' + source + ' ' + str(target), str(image)]
    result = subprocess.run(command, capture_output=True, check=True)
    (report / (name + '.stdout')).write_bytes(result.stdout)
    (report / (name + '.stderr')).write_bytes(result.stderr)
    commands.append(command)
rows = []
files = []
for path in sorted(root.rglob('*.cfg')):
    raw = path.read_bytes()
    files.append(dict(path=str(path.relative_to(root)), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest()))
    try: data = json.loads(raw)
    except (ValueError, UnicodeDecodeError): continue
    for job in data.get('jobs', []):
        matches = [cmd for cmd in job.get('cmds', []) if any(x in cmd for x in ['/bms', 'bundle_manager_service', 'post-fs-data', 'load_dac'])]
        if matches: rows.append(dict(path=str(path.relative_to(root)), job=job.get('name'), condition=job.get('condition'), commands=matches))
assert files, 'no actual init config files extracted'
after = {str(p): digest(p) for p in images}
assert before == after
result = dict(original_images_before=before, original_images_after=after,
              original_images_unchanged=True, target_code_executed=False,
              commands=commands, config_files=files, relevant_jobs=rows)
(report / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(dict(files=len(files), relevant_jobs=rows), indent=2))
'''

if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
