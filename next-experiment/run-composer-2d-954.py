"""Compare the identical KMS fixture against reference non-GL VirtIO scanout."""
from pathlib import Path
import json

base = Path(__file__).resolve().parent
parent = base / 'official-composer-kms-952'
assert json.loads((base / 'official-composer-capture-953/result.json').read_text())['probe_pass']
out = base / 'official-composer-2d-954'
assert not out.exists()
source = (base / 'run-composer-kms-952.py').read_text()
source = source.replace("out = base / 'official-composer-kms-952'", "out = base / 'official-composer-2d-954'")
source = source.replace('composer-kms-runtime-952', 'composer-2d-runtime-954')
anchor = "gpu='/home/zoinve/.local/share/harmony-arm64-kvm-lab/gpu-host-probe-883'"
assert source.count(anchor) == 1
source = source.replace(anchor, "cmd[cmd.index('-display')+1]='none'\ncmd=[arg.replace('virtio-gpu-gl-pci','virtio-gpu-pci') for arg in cmd]\n" + anchor)
compile(source, 'composer-2d-954', 'exec')
out.mkdir()
for name in ('manifest.json', 'initramfs.cpio.gz'):
    (out / name).write_bytes((parent / name).read_bytes())
exec(compile(source, 'composer-2d-954', 'exec'))
