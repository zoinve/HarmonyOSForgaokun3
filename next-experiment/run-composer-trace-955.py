"""Instrument unchanged 952 GPU transport without changing guest or composer."""
from pathlib import Path
import subprocess

base = Path(__file__).resolve().parent
parent = base / 'official-composer-kms-952'
out = base / 'official-composer-trace-955'
assert not out.exists()
source = (base / 'run-composer-kms-952.py').read_text()
source = source.replace("out = base / 'official-composer-kms-952'", "out = base / 'official-composer-trace-955'")
source = source.replace('composer-kms-runtime-952', 'composer-trace-runtime-955')
anchor = "gpu='/home/zoinve/.local/share/harmony-arm64-kvm-lab/gpu-host-probe-883'"
assert source.count(anchor) == 1
source = source.replace(anchor,
    "(o/'trace-events').write_text('virtio_gpu_cmd_set_scanout\\nvirtio_gpu_cmd_res_flush\\n')\n"
    "cmd += ['-trace', 'events='+str(o/'trace-events')+',file='+str(o/'gpu-transport.trace')]\n" + anchor)
compile(source, 'composer-trace-955', 'exec')
out.mkdir()
for name in ('manifest.json', 'initramfs.cpio.gz'):
    (out / name).write_bytes((parent / name).read_bytes())
exec(compile(source, 'composer-trace-955', 'exec'))
subprocess.run(['scp', 'matebook:/home/zoinve/.local/share/harmony-arm64-kvm-lab/official-arm-sdk-921/composer-trace-runtime-955/gpu-transport.trace',
                str(out / 'gpu-transport.trace')], check=True)
