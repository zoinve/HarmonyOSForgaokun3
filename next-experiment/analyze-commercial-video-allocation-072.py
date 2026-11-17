"""Preserve the newly reached original-service allocation failure separately."""
from pathlib import Path
import hashlib
import json

base = Path(__file__).resolve().parents[1]
report = base / 'reports/commercial61-native-072'
raw = report / 'runtime-evidence/raw'
manifest = json.loads((raw.parent / 'retrieval-manifest.json').read_text())
for name, item in manifest['files'].items():
    data = (raw / name).read_bytes()
    assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256']
lines = (raw / 'interactive-hilog030.log').read_text(errors='replace').splitlines()
patterns = dict(codec_surface_allocation_failed='Alloc surface buffer failed',
    codec_start_allocation_failed='Start codec failed: cannot allocate buffers',
    allocator_service_minus_two='AllocMem: AllocMem failed, ec = -2',
    allocator_proxy_minus_two='AllocMem_ failed, error code is -2',
    combined_consumer_usage='Usage: default(0x11) | consumer(0x1032) | cfged(0x11) -> final(0x1035).')
matched = {name: [line for line in lines if text in line] for name, text in patterns.items()}
reference = Path('C:/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/graphics')
if not reference.exists():
    reference = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/graphics')
source = (reference / 'buffer_vdi.cpp').read_text()
interface = (reference / 'include/idisplay_buffer_vdi.h').read_text()
assert '#define NOT_SUPPORT (-2)' in interface
assert 'format != PIXEL_FMT_RGBX_8888 && format != PIXEL_FMT_RGBA_8888' in source
assert 'format != PIXEL_FMT_BGRX_8888 && format != PIXEL_FMT_BGRA_8888' in source
result = dict(run=manifest['run'], verified_files=len(manifest['files']),
    counts={name: len(rows) for name, rows in matched.items()}, matched_messages=matched,
    reference_source_sha256=hashlib.sha256((reference / 'buffer_vdi.cpp').read_bytes()).hexdigest(),
    reference_interface_sha256=hashlib.sha256((reference / 'include/idisplay_buffer_vdi.h').read_bytes()).hexdigest(),
    reference_allocator_accepts_only_four_rgb_formats=True, reference_not_support_value=-2,
    actual_failed_request_format_observed=False, allocator_host_effective_maps_captured=False,
    allocator_backend_rejection_is_hypothesis_not_proven_cause=True,
    app_namespace_helper_logs_absent_does_not_prove_helper_failure=True,
    native_harmonyos_decoded_frames_verified=False, desktop_verified=False, interaction_verified=False)
with (report / 'video-allocation-analysis.json').open('x') as f:
    json.dump(result, f, indent=2)
print(json.dumps({k: v for k, v in result.items() if k != 'matched_messages'}, indent=2))
