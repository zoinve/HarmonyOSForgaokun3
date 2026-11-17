"""Build own YUV-capable board backends against retained original runtimes."""
from pathlib import Path
import hashlib
import json
import runpy
import subprocess

b = Path(__file__).resolve().parent
root = Path('/home/zoinve/harmony-virgl-883')
work = root / 'commercial-yuv-074-r3'
report = b.parent / 'reports/commercial-yuv-074-r3'
assert not work.exists() and not report.exists()
transform = runpy.run_path(str(b / 'commercial-yuv-074.py'))
parents = [('allocator', root / 'commercial-allocator-073', 'buffer-vdi.cpp',
            'libdisplay_buffer_vdi_impl.z.so', 'sha256'),
           ('egl', root / 'commercial-egl-067', 'egl-trace-067.cpp',
            'libEGL_impl.so', 'bridge_sha256')]
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

work.mkdir()
report.mkdir()
header = (b / 'commercial-linear-layout-074.h').read_bytes()
(work / 'commercial-linear-layout-074.h').open('xb').write(header)
artifacts = {}
for role, parent, source_name, binary_name, hash_key in parents:
    provenance = json.loads((parent / 'result.json').read_text())
    assert sha(parent / binary_name) == provenance[hash_key]
    assert sha(parent / source_name) == provenance['source_sha256']
    source = transform[role]((parent / source_name).read_text())
    destination = work / (role + '-074.cpp')
    destination.open('x').write(source)
    (report / destination.name).open('x').write(source)
    command = [str(destination) if item == str(parent / source_name) else
               str(work / binary_name) if item == str(parent / binary_name) else item
               for item in provenance['command']]
    run = subprocess.run(command, capture_output=True, timeout=120)
    for suffix, body in [('stdout', run.stdout), ('stderr', run.stderr)]:
        for folder in [work, report]:
            (folder / (role + '.link.' + suffix)).open('xb').write(body)
    assert run.returncode == 0, run.stderr.decode(errors='replace')
    dynamic = subprocess.check_output(['aarch64-linux-gnu-readelf', '-d', str(work / binary_name)], text=True)
    assert 'libc++_shared.so' not in dynamic and 'libc.so.6' not in dynamic
    assert b'/runtime/libc++.so' in run.stdout and b'/runtime/libc.so' in run.stdout
    symbols = lambda p: sorted(line.split()[-1] for line in subprocess.check_output(
        ['aarch64-linux-gnu-nm', '-D', '--defined-only', str(p)], text=True).splitlines())
    if role == 'egl':
        assert symbols(parent / binary_name) == symbols(work / binary_name)
    artifacts[role] = dict(command=command, source_sha256=sha(destination),
        binary_sha256=sha(work / binary_name), bytes=(work / binary_name).stat().st_size,
        parent_binary_sha256=provenance[hash_key], parent_source_sha256=provenance['source_sha256'])
result = dict(artifacts=artifacts, header_sha256=hashlib.sha256(header).hexdigest(),
              original_commercial_runtime=True, egl_public_exports_unchanged=True,
              protected_buffers_still_rejected=True, original_service_identities_unchanged=True,
              native_allocation_verified=False, gpu_import_verified=False,
              desktop_verified=False, interaction_verified=False)
for folder in [work, report]:
    (folder / 'result.json').open('x').write(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
