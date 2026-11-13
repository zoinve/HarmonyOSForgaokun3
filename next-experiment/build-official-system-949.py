"""Fresh full-system diagnostic copy with tested DRM-selection tracing only."""
from pathlib import Path

base = Path(__file__).resolve().parent
source = (base / 'build-official-system-944.py').read_text()
replacements = {
    'official-display-capability-943/result.json': 'official-drm-boundary-948/result.json',
    "('child_exit_zero', 'default_selected', 'native_present_pass')": "('child_exit_zero', 'drm_selected', 'native_present_pass')",
    'official-system-944': 'official-system-949',
    'official-system-941/manifest.json': 'official-system-947/manifest.json',
    'official-display-capability-943/initramfs.cpio.gz': 'official-drm-boundary-948/initramfs.cpio.gz',
    '1fcb2dd4be736dd1401218efcea7d900c6dc416c208076ecbbdc10edd394b8b0': 'fb54e339d2fa7c3d0387b2ac8b70ebf89c795569bd328f8876f8f904012593d5',
    '20426afb3254aced34486dc5d13fc7502d74a256f5c63f39ad9e607fe247af4d': '21f524e924d1c3841575171e6256e6f57e870e9816cc6c8ba605016c74f97258',
}
for old, new in replacements.items():
    assert old in source, old
    source = source.replace(old, new)
exec(compile(source, 'build-system-949-generated', 'exec'))
