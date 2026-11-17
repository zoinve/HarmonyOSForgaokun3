"""Rebuild the same own allocator with request logging, not format changes."""
from pathlib import Path
import hashlib
import json
import runpy
import subprocess

base = Path(__file__).resolve().parent
root = Path('/home/zoinve/harmony-virgl-883')
old = root / 'commercial-allocator-015'
work = root / 'commercial-allocator-073'
report = base.parent / 'reports/commercial-allocator-073'
work.mkdir()
report.mkdir()
previous = json.loads((old / 'result.json').read_text())
assert hashlib.sha256((old / 'libdisplay_buffer_vdi_impl.z.so').read_bytes()).hexdigest() == previous['sha256']
reference = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816/ports/graphics/buffer_vdi.cpp')
assert hashlib.sha256(reference.read_bytes()).hexdigest() == previous['reference_source_sha256']
expected = reference.read_text().replace('info.usage), info.expectedSize);', 'info.usage), static_cast<size_t>(info.expectedSize));')
expected = expected.replace('size mismatch got=%u expected=%zu', 'size mismatch got=%llu expected=%zu')
expected = expected.replace('request.size, info.expectedSize);', 'static_cast<unsigned long long>(request.size), static_cast<size_t>(info.expectedSize));')
assert (old / 'buffer-vdi.cpp').read_text() == expected
instrument = runpy.run_path(str(base / 'commercial-allocator-observer-073.py'))
source = instrument['allocator'](expected)
with (work / 'buffer-vdi.cpp').open('x') as f:
    f.write(source)
command = [str(work / 'buffer-vdi.cpp') if item == str(old / 'buffer-vdi.cpp') else
    str(work / 'libdisplay_buffer_vdi_impl.z.so') if item == str(old / 'libdisplay_buffer_vdi_impl.z.so') else item
    for item in previous['commands'][0]]
run = subprocess.run(command, capture_output=True, timeout=120)
for name, data in [('link.stdout', run.stdout), ('link.stderr', run.stderr)]:
    for directory in [work, report]:
        with (directory / name).open('xb') as f:
            f.write(data)
assert run.returncode == 0, run.stderr.decode(errors='replace')
body = (work / 'libdisplay_buffer_vdi_impl.z.so').read_bytes()
dynamic = subprocess.check_output(['aarch64-linux-gnu-readelf', '-d', str(work / 'libdisplay_buffer_vdi_impl.z.so')], text=True)
assert 'libc++_shared.so' not in dynamic and 'libc.so.6' not in dynamic
assert str(old / 'runtime/libc++.so').encode() in run.stdout
assert str(old / 'runtime/libc.so').encode() in run.stdout
record = dict(sha256=hashlib.sha256(body).hexdigest(), bytes=len(body), command=command,
    parent_allocator_sha256=previous['sha256'], reference_source_sha256=previous['reference_source_sha256'],
    source_sha256=hashlib.sha256(source.encode()).hexdigest(), exact_public_logging_only=True,
    allocator_return_values_unchanged=True, format_support_unchanged=True,
    original_commercial_runtime=True, original_service_identity_unchanged=True,
    runtime_verified=False, desktop_verified=False)
for directory in [work, report]:
    with (directory / 'result.json').open('x') as f:
        json.dump(record, f, indent=2)
print(json.dumps(record, indent=2))
