"""Single-variable comparison: fresh 2 GiB userdata; all 950 guest settings retained."""
from pathlib import Path
import json
import subprocess

base = Path(__file__).resolve().parent
parent = base / 'official-arm-run-950'
out = base / 'official-arm-run-951'
remote = '/home/zoinve/.local/share/harmony-arm64-kvm-lab/official-arm-sdk-921/full-system-951'
flags = ('readonly_inputs_unchanged', 'official_originals_unchanged', 'protected_userdata_original_unchanged')
assert all(json.loads((parent / 'result.json').read_text())[k] for k in flags)
assert (base.parent / 'reports/userdata-cleanup-official-950.json').is_file()
assert not out.exists()
c = json.loads((parent / 'config.json').read_text())
c['command'] = [arg.replace('full-system-950/', 'full-system-951/') for arg in c['command']]
for row in c['inputs']:
    row['remote'] = row['remote'].replace('full-system-950/', 'full-system-951/')
c['disks'][3]['path'] = remote + '/userdata-permissive.img'
c['userdata_capacity_bytes'] = 2 * 1024 ** 3
source = (parent / 'runner.py').read_text().replace('full-system-950', 'full-system-951')
anchor = "shutil.copyfile(Path(c['originals'][3]['path']),work)"
assert source.count(anchor) == 1
growth = """
# Grow only this experiment's fresh writable copy, before QEMU starts.
assert work.parent == o and work.stat().st_size == 104857600
with work.open('r+b') as stream: stream.truncate(2 * 1024 ** 3)
subprocess.run(['resize2fs', str(work)], check=True, capture_output=True)
check = subprocess.run(['e2fsck', '-fn', str(work)], capture_output=True, text=True)
assert check.returncode == 0, check.stdout + check.stderr
c['disks'][3].update(bytes=work.stat().st_size, sha256=sha(work))
assert c['disks'][3]['bytes'] == 2 * 1024 ** 3
(o/'userdata-capacity-check.txt').write_text(check.stdout + check.stderr)
(o/'config.json').write_text(json.dumps(c, indent=2))
d['userdata_capacity_bytes'] = c['disks'][3]['bytes']
"""
source = source.replace(anchor, anchor + '\n' + growth)
compile(source, 'runner-951', 'exec')
assert ' enforcing=0' in c['command'][c['command'].index('-append') + 1]
assert c['originals'] == json.loads((parent / 'config.json').read_text())['originals']
assert sum('readonly=on' in arg for arg in c['command']) == 3
subprocess.run(['ssh', 'matebook', 'mkdir ' + remote], check=True)
out.mkdir()
(out / 'config.json').write_text(json.dumps(c, indent=2))
(out / 'runner.py').write_text(source)
for path, name in [(out / 'config.json', 'config.json'), (out / 'runner.py', 'runner.py'),
                   (base / 'official-arm-mount-921/initramfs.cpio.gz', 'initramfs.cpio.gz')]:
    subprocess.run(['scp', str(path), 'matebook:' + remote + '/' + name], check=True)
with (out / 'host.stdout').open('xb') as stdout, (out / 'host.stderr').open('xb') as stderr:
    result = subprocess.run(['ssh', 'matebook', 'sudo -n python3 ' + remote + '/runner.py'],
                            stdout=stdout, stderr=stderr, timeout=900)
for name in ('result.json', 'serial.log', 'stderr.log', 'config.json', 'userdata-capacity-check.txt'):
    subprocess.run(['scp', 'matebook:' + remote + '/' + name, str(out / name)], check=True)
d = json.loads((out / 'result.json').read_text())
for shot in d['screenshots']:
    subprocess.run(['scp', 'matebook:' + remote + '/' + shot['name'], str(out / shot['name'])], check=True)
print(json.dumps({k: d.get(k) for k in ('returncode', 'elapsed_seconds', 'screenshots', 'userdata_capacity_bytes') + flags}, indent=2))
assert result.returncode == 0 and all(d[k] for k in flags)
