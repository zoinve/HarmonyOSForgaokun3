"""Fresh diagnostic full-system copy; only our tested EGL logger changes."""
from pathlib import Path
import json

base = Path(__file__).resolve().parent
trial = json.loads((base / 'official-skia-context-946/result.json').read_text())
assert all(trial[k] for k in ('child_exit_zero', 'skia_context_pass', 'native_present_pass'))
source = (base / 'build-official-system-944.py').read_text()
replacements = {
    "official-display-capability-943/result.json": "official-skia-context-946/result.json",
    "('child_exit_zero', 'default_selected', 'native_present_pass')": "('child_exit_zero', 'skia_context_pass', 'native_present_pass')",
    "official-system-944": "official-system-947",
    "official-system-941/manifest.json": "official-system-944/manifest.json",
    "official-display-capability-943/initramfs.cpio.gz": "official-egl-boundary-945/initramfs.cpio.gz",
    "1fcb2dd4be736dd1401218efcea7d900c6dc416c208076ecbbdc10edd394b8b0": "58ed43d5b7ab42fd24a26fda4d72a53c748d28f22c926bd199f91d5bda6ce281",
    "20426afb3254aced34486dc5d13fc7502d74a256f5c63f39ad9e607fe247af4d": "bd479cbfad98d9681be6e1ee7f72ccc815d456c2d077301501a2507d833440b4",
}
for old, new in replacements.items():
    assert old in source, old
    source = source.replace(old, new)
exec(compile(source, 'build-system-947-generated', 'exec'))
