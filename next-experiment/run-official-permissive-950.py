"""Authorized SELinux-only boot comparison; reuse immutable 949 graphics disks."""
from pathlib import Path

base = Path(__file__).resolve().parent
source = (base / 'run-official-graphics-941.py').read_text()
assert source.count('941') == 5
source = source.replace('941', '950')
changes = {
    "base / 'official-system-950/manifest.json'": "base / 'official-system-949/manifest.json'",
    "remote + '/' + name + '-graphics.img'": "m.LAB + '/official-arm-sdk-921/full-system-949/' + name + '-graphics.img'",
    "c = m.build_config(originals, remote)": "c = m.build_config(originals, remote)\nc['command'][c['command'].index('-append') + 1] += ' enforcing=0'\nc['selinux_mode_requested'] = 'permissive; explicitly authorized by user'",
    "source = source.replace('selinux_permissive_authorized=True', 'selinux_permissive_authorized=False')": "source = source.replace('selinux_permissive_authorized=True', 'selinux_permissive_authorized=True')",
}
for old, new in changes.items():
    assert source.count(old) == 1, old
    source = source.replace(old, new)
# Keep normal service protections. Earlier headless captures aid short-boot diagnosis.
anchor = "compile(source, 'runner-950', 'exec')"
assert source.count(anchor) == 1
source = source.replace(anchor,
    "source = source.replace('next_shot=60;', 'next_shot=15;')\n"
    "source = source.replace('next_shot=180 if next_shot==60 else next_shot+120', 'next_shot=next_shot+30')\n" + anchor)
exec(compile(source, 'permissive-950-launcher', 'exec'))
