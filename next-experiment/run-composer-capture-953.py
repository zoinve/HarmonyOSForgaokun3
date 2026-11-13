"""Capture-sink comparison only: identical 952 archive/GPU plus Unix-only VNC."""
from pathlib import Path
import json

base = Path(__file__).resolve().parent
parent = base / 'official-composer-kms-952'
previous = json.loads((parent / 'result.json').read_text())
assert previous['probe_pass'] and previous['four_real_frames'] and previous['child_exit_zero']
assert previous['screenshot_error'].find('no surface') >= 0
out = base / 'official-composer-capture-953'
assert not out.exists()
source = (base / 'run-composer-kms-952.py').read_text()
source = source.replace("out = base / 'official-composer-kms-952'", "out = base / 'official-composer-capture-953'")
source = source.replace('composer-kms-runtime-952', 'composer-capture-runtime-953')
anchor = "gpu='/home/zoinve/.local/share/harmony-arm64-kvm-lab/gpu-host-probe-883'"
assert source.count(anchor) == 1
source = source.replace(anchor, "cmd += ['-vnc', 'unix:'+str(o/'vnc.sock')]\n" + anchor)
compile(source, 'capture-953', 'exec')
out.mkdir()
for name in ('manifest.json', 'initramfs.cpio.gz'):
    (out / name).write_bytes((parent / name).read_bytes())
exec(compile(source, 'capture-953', 'exec'))
