"""Validate exported pixels and report guide dismissal without assuming a desktop."""
from pathlib import Path
import hashlib
import json
import re
import runpy
import sys

b = Path(__file__).resolve().parent
number = sys.argv[1] if len(sys.argv) == 2 else '075'
assert number in ['074', '075']
root = b.parent / ('reports/commercial61-native-' + number)
raw = root / 'runtime-evidence/raw'
manifest = json.loads((raw.parent / 'retrieval-manifest.json').read_text())
for name, item in manifest['files'].items():
    body = (raw / name).read_bytes()
    assert len(body) == item['bytes'] and hashlib.sha256(body).hexdigest() == item['sha256']
phase = max(raw.glob('phase-*.log'), key=lambda p: int(p.stem.split('-')[1])).read_bytes()
helper = runpy.run_path(str(b / 'native-ppm-evidence-068.py'))
out = root / 'desktop-pixel-review'
out.mkdir()
result = dict(run=manifest['run'], verified_files=len(manifest['files']), images={},
              desktop_verified=False, interaction_verified=False, activation_verified=False)
views = {}
for tag, marker in [('before-input', '068'), ('after-input', '075')]:
    ready = raw / ('full-ready-' + marker)
    if not ready.exists():
        result['images'][tag] = dict(missing=True)
        continue
    match = re.fullmatch(rb'FULL068_READY source_bytes=(\d+) output_bytes=(\d+) mono_us=(\d+) fb=(\d+)\n', ready.read_bytes())
    assert match
    source_size, output_size, mono, fb = map(int, match.groups())
    assert 120000000 <= mono < 145000000 and fb > 0
    if marker == '075':
        assert mono >= 140000000
        export = rb'COMMERCIAL075_SECOND_FULL_EXPORT child=\d+ status=0 deadline_ms=8000'
    else:
        export = ('COMMERCIAL' + number + '_FULL_EXPORT child=\\d+ status=0 deadline_ms=8000').encode()
    assert re.search(export, phase), 'No successful bounded export record'
    frames = {}
    for role, expected in [('source', source_size), ('output', output_size)]:
        body = (raw / ('full-' + role + '-' + marker + '.ppm')).read_bytes()
        assert len(body) == expected
        width, height, pixels = helper['parse_ppm'](body)
        assert (width, height) == ((2560, 1600) if role == 'source' else (1600, 2560))
        png = helper['png_bytes'](width, height, pixels)
        (out / (tag + '-' + role + '.png')).open('xb').write(png)
        frames[role] = dict(ppm_sha256=hashlib.sha256(body).hexdigest(),
                            png_sha256=hashlib.sha256(png).hexdigest(),
                            **helper['pixel_stats'](width, height, pixels))
        views[tag, role] = (width, height, pixels)
    sw, sh, source = views[tag, 'source']
    ow, oh, output = views[tag, 'output']
    different = sum(output[(y*ow+x)*3:(y*ow+x+1)*3] != source[((sh-1-x)*sw+y)*3:((sh-1-x)*sw+y+1)*3]
                    for y in range(oh) for x in range(ow))
    result['images'][tag] = dict(mono_us=mono, fb=fb, frames=frames,
                                clockwise_rotation_different_pixels=different,
                                original_trace_stream_not_required_for_independent_export_validation=True)
if ('before-input', 'source') in views and ('after-input', 'source') in views:
    before, after = views['before-input', 'source'][2], views['after-input', 'source'][2]
    result['changed_source_pixels'] = sum(before[i:i+3] != after[i:i+3] for i in range(0, len(before), 3))
command = raw / 'snapshot075-commercial-direct-desktop075.log'
if command.exists():
    text = command.read_text(errors='replace')
    result['guide_commands'] = dict(
        start_results=re.findall(r'COMMERCIAL075_START_RESULT result=(\d+)', text),
        stop_results=re.findall(r'COMMERCIAL075_GUIDE_STOP_RESULT result=(\d+)', text),
        guide_pid_results=re.findall(r'COMMERCIAL075_GUIDE_PID_RESULT result=(\d+)', text),
        scene_pid_results=re.findall(r'COMMERCIAL075_SCENE_PID_RESULT result=(\d+)', text),
        commands_done='COMMERCIAL075_COMMANDS_DONE' in text,
        start_failure_text='error: failed to start ability.' in text,
        stop_failure_text='error: failed to force stop process.' in text,
        caller_identity_lines=[line for line in text.splitlines() if line.startswith('uid=')],
        cli_exit_zero_is_not_operation_success=True,
        failure_is_not_activation_or_desktop_success=True)
else:
    result['guide_commands'] = dict(missing=True)
result['keyboard_records'] = [line.decode(errors='replace') for line in phase.splitlines() if line.startswith(b'COMMERCIAL075_KEYBOARD ')]
result['target_exit_records'] = [line.decode(errors='replace') for line in phase.splitlines()
                                  if re.match(rb'COMMERCIAL\d+(_TARGET_EXIT| target_timeout| fallback_reboot)', line)]
(out / 'result.json').open('x').write(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
