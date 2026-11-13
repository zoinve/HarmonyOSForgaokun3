"""Standalone runner; use a new experiment number. Never writes the original disks."""
from pathlib import Path
import argparse, hashlib, json, subprocess

base = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('number', type=int)
parser.add_argument('--on-screen', action='store_true', help='Open a local viewer on the MateBook display for 30 minutes')
parser.add_argument('--quiet-trace', action='store_true', help='Keep tracing but disable its serial printk flood')
parser.add_argument('--relative-mouse', action='store_true', help='Use a standard relative USB mouse instead of the absolute tablet')
parser.add_argument('--initramfs', type=Path, help='Use a separately built RAM payload, copied and hash-pinned for this fresh run')
parser.add_argument('--duration', type=int, help='Bounded observation seconds (60–1800), independent of physical viewing')
parser.add_argument('--diagnostic-resolution', choices=['960x540'], help='Opt-in quarter-pixel-count rendering diagnostic; default stays 1920x1080')
parser.add_argument('--virgl', action='store_true', help='Use isolated, previously verified headless VirGL host modules')
parser.add_argument('--user-network', action='store_true', help='Opt into normal outbound guest NAT, without inbound port forwarding')
parser.add_argument('--hdc-port', type=int, help='Optional host-loopback-only ingress to the original guest HDC TCP port')
args = parser.parse_args()
if args.hdc_port is not None:
    assert args.user_network and 1024 <= args.hdc_port <= 65535
if args.duration is not None:
    assert 60 <= args.duration <= 1800
assert args.number >= 870, 'Use a fresh number, 870 or higher'
remote = f'/home/zoinve/.local/share/harmony-arm64-kvm-lab/system-{args.number}'
out = base / f'run-{args.number}'
assert not out.exists()
c = json.loads((base / 'config-template.json').read_text())
c['command'] = [s.replace('/system-868/', f'/system-{args.number}/') for s in c['command']]
for row in c['disks']:
    row['path'] = row['path'].replace('/system-868/', f'/system-{args.number}/')
c['inputs'][0]['remote'] = remote + '/Image'
if args.user_network:
    i = c['command'].index('-nic')
    assert c['command'][i + 1] == 'none'
    c['command'][i:i + 2] = ['-netdev', 'user,id=normalnet', '-device', 'virtio-net-device,netdev=normalnet']
    if args.hdc_port is not None:
        c['command'][i + 1] += f',hostfwd=tcp:127.0.0.1:{args.hdc_port}-10.0.2.15:8710'
gpu = c['command'].index('virtio-gpu-pci')
c['command'][gpu] = 'virtio-gpu-pci,xres=1920,yres=1080'
if args.diagnostic_resolution:
    width, height = args.diagnostic_resolution.split('x')
    c['command'][gpu] = f'virtio-gpu-pci,xres={width},yres={height}'
if args.virgl:
    assert not args.on_screen, 'VirGL experiments remain headless'
    c['qmp_screenshots_enabled'] = False
    c['command'][gpu] = c['command'][gpu].replace('virtio-gpu-pci,', 'virtio-gpu-gl-pci,')
    c['command'][c['command'].index('-display') + 1] = 'egl-headless,rendernode=/dev/dri/renderD128'
if args.relative_mouse:
    assert c['command'].count('usb-tablet') == 1
    c['command'][c['command'].index('usb-tablet')] = 'usb-mouse'
if args.quiet_trace:
    i = c['command'].index('-append') + 1
    tokens = c['command'][i].split()
    assert tokens.count('tp_printk') == 1
    c['command'][i] = ' '.join('tp_printk=0' if token == 'tp_printk' else token for token in tokens)
for name, index in [('Image', 0), ('initramfs.cpio.gz', 1)]:
    assert hashlib.sha256((base / name).read_bytes()).hexdigest() == c['inputs'][index]['sha256']
if args.initramfs:
    assert args.initramfs.is_file()
    target = remote + '/initramfs.cpio.gz'
    c['command'][c['command'].index('-initrd') + 1] = target
    c['inputs'][1] = dict(remote=target, sha256=hashlib.sha256(args.initramfs.read_bytes()).hexdigest())
source = (base / 'runner-template.py').read_text().replace('/system-868', f'/system-{args.number}')
if args.virgl:
    anchor = 'vm=subprocess.Popen(cmd,stdout=serial,stderr=err)'
    assert source.count(anchor) == 1
    host = '/home/zoinve/.local/share/harmony-arm64-kvm-lab/gpu-host-probe-883'
    setup = "import os; qemu_env=os.environ.copy(); qemu_env.update(" + repr({
        'QEMU_MODULE_DIR': host + '/modules',
        'LD_LIBRARY_PATH': host + '/root/usr/lib/aarch64-linux-gnu',
    }) + "); "
    source = source.replace(anchor, setup + 'vm=subprocess.Popen(cmd,stdout=serial,stderr=err,env=qemu_env)')
duration = args.duration if args.duration is not None else (1800 if args.on_screen else 360)
source = source.replace('elapsed>=360', f'elapsed>={duration}').replace('wall_limit_seconds=360', f'wall_limit_seconds={duration}')
if args.on_screen:
    anchor = "  qmp({'execute':'cont'});d['guest_started']=True"
    assert source.count(anchor) == 1
    viewer = '''
   import os, pwd
   user=pwd.getpwnam('zoinve')
   envtext=subprocess.check_output(['sudo','-u','zoinve','env','XDG_RUNTIME_DIR=/run/user/'+str(user.pw_uid),'systemctl','--user','show-environment'],text=True)
   desktop_env=dict(line.split('=',1) for line in envtext.splitlines() if '=' in line)
   assert desktop_env.get('DISPLAY') and desktop_env.get('XAUTHORITY'), 'No active graphical desktop'
   sock=o/'vnc.sock';os.chown(sock,user.pw_uid,user.pw_gid);os.chmod(sock,0o600)
   viewer_cmd=['sudo','-u','zoinve','env',*[k+'='+v for k,v in desktop_env.items()],'/usr/bin/python3',str(o/'scaled-viewer.py'),str(sock)]
   with (o/'viewer.log').open('xb') as viewer_log:
    viewer_proc=subprocess.Popen(viewer_cmd,stdout=viewer_log,stderr=viewer_log,start_new_session=True)
   d['physical_screen_viewer_pid']=viewer_proc.pid
'''
    viewer = '\n'.join(line[1:] if line.startswith(' ') else line for line in viewer.split('\n'))
    source = source.replace(anchor, anchor + viewer)
compile(source, 'remote-runner', 'exec')
subprocess.run(['ssh', 'matebook', 'mkdir ' + remote], check=True)
out.mkdir()
(out / 'config.json').write_text(json.dumps(c, indent=2))
(out / 'runner.py').write_text(source)
for local, target in [(out / 'config.json', remote + '/config.json'), (out / 'runner.py', remote + '/runner.py'), (base / 'Image', remote + '/Image')]:
    subprocess.run(['scp', str(local), 'matebook:' + target], check=True)
if args.initramfs:
    subprocess.run(['scp', str(args.initramfs), 'matebook:' + c['inputs'][1]['remote']], check=True)
if args.on_screen:
    subprocess.run(['scp', str(base / 'scaled-viewer.py'), 'matebook:' + remote + '/scaled-viewer.py'], check=True)
r = subprocess.run(['ssh', 'matebook', 'sudo -n python3 ' + remote + '/runner.py'], capture_output=True, timeout=max(1800, duration + 1800))
(out / 'host.stdout').write_bytes(r.stdout)
(out / 'host.stderr').write_bytes(r.stderr)
for name in ['result.json', 'serial.log', 'stderr.log']:
    subprocess.run(['scp', 'matebook:' + remote + '/' + name, str(out / name)], check=True)
d = json.loads((out / 'result.json').read_text())
for shot in d['screenshots']:
    subprocess.run(['scp', 'matebook:' + remote + '/' + shot['name'], str(out / shot['name'])], check=True)
assert r.returncode == 0 and d['readonly_inputs_unchanged'] and d['protected_userdata_original_unchanged']
print(json.dumps({k: d.get(k) for k in ['returncode', 'readonly_inputs_unchanged', 'protected_userdata_original_unchanged']}, indent=2))
