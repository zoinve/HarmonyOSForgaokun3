"""Correct host tool discovery; preserve the failed 001 directory unchanged."""
from pathlib import Path

base = Path(__file__).resolve().parent
source = (base / 'prepare-baremetal-initramfs-base-001.py').read_text()
assert source.count('initramfs-base-001') == 2
source = source.replace('initramfs-base-001', 'initramfs-base-002')
anchor = "checks=[]\ncommands="
assert source.count(anchor) == 1
source = source.replace(anchor,
    "chroot=shutil.which('chroot')\nassert chroot and Path(chroot).is_file(), 'Host chroot tool missing'\n" + anchor)
anchor = "['/usr/sbin/chroot',str(root)]"
assert source.count(anchor) == 1
source = source.replace(anchor, "[chroot,str(root)]")
exec(compile(source, 'prepare-baremetal-initramfs-base-002-generated', 'exec'))
