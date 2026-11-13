"""Bounded full-system trial; run only after immutable 941 copies are staged."""
from pathlib import Path
import importlib.util
import json
import subprocess

base = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('official', base / 'official-arm-config.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
remote = m.LAB + '/official-arm-sdk-921/full-system-941'
out = base / 'official-arm-run-941'
assert not out.exists()
originals = [dict(name=r['name'], path=r['remote'], bytes=r['size'], sha256=r['sha256'])
             for r in json.loads((base.parent / 'reports/official-arm-sdk-921-inputs.json').read_text())['files']]
adapted = json.loads((base / 'official-system-941/manifest.json').read_text())['images']
c = m.build_config(originals, remote)
for i, name in enumerate(['system', 'vendor']):
    row = c['disks'][i]
    old = row['path']
    row.update(path=remote + '/' + name + '-graphics.img', sha256=adapted[i]['sha256'])
    c['command'] = [arg.replace(old, row['path']) for arg in c['command']]
cmd = c['command']
cmd[cmd.index('-display') + 1] = 'egl-headless,rendernode=/dev/dri/renderD128'
cmd[cmd.index('virtio-gpu-pci,xres=1920,yres=1080')] = 'virtio-gpu-gl-pci,xres=1920,yres=1080'
c['qmp_screenshots_enabled'] = True
source = m.make_runner(remote, base / 'runner-template.py')
source = source.replace('import json,subprocess,socket,time,hashlib', 'import json,subprocess,socket,time,hashlib,os')
anchor = 'subprocess.Popen(cmd,stdout=serial,stderr=err)'
assert source.count(anchor) == 1
gpu = m.LAB + '/gpu-host-probe-883'
source = source.replace(anchor, f"subprocess.Popen(cmd,stdout=serial,stderr=err,env=dict(os.environ,QEMU_MODULE_DIR='{gpu}/modules',LD_LIBRARY_PATH='{gpu}/root/usr/lib/aarch64-linux-gnu'))")
source = source.replace('selinux_permissive_authorized=True', 'selinux_permissive_authorized=False')
source = source.replace('bounded_360s_authorized_permissive_explicit_start', 'bounded_360s_official_graphics_trial')
compile(source, 'runner-941', 'exec')
assert c['originals'] == originals and sum('readonly=on' in arg for arg in cmd) == 3
out.mkdir()
(out / 'config.json').write_text(json.dumps(c, indent=2))
(out / 'runner.py').write_text(source)
for path, name in [(out / 'config.json', 'config.json'), (out / 'runner.py', 'runner.py'),
                   (base / 'official-arm-mount-921/initramfs.cpio.gz', 'initramfs.cpio.gz')]:
    subprocess.run(['scp', str(path), 'matebook:' + remote + '/' + name], check=True)
with (out / 'host.stdout').open('xb') as stdout, (out / 'host.stderr').open('xb') as stderr:
    r = subprocess.run(['ssh', 'matebook', 'sudo -n python3 ' + remote + '/runner.py'],
                       stdout=stdout, stderr=stderr, timeout=900)
for name in ['result.json', 'serial.log', 'stderr.log']:
    subprocess.run(['scp', 'matebook:' + remote + '/' + name, str(out / name)], check=True)
d = json.loads((out / 'result.json').read_text())
for shot in d['screenshots']:
    subprocess.run(['scp', 'matebook:' + remote + '/' + shot['name'], str(out / shot['name'])], check=True)
print(json.dumps({k: d.get(k) for k in ['returncode', 'elapsed_seconds', 'screenshots',
      'readonly_inputs_unchanged', 'official_originals_unchanged', 'protected_userdata_original_unchanged']}, indent=2))
assert r.returncode == 0
assert all(d[k] for k in ['readonly_inputs_unchanged', 'official_originals_unchanged', 'protected_userdata_original_unchanged'])
