"""Public bounded requests, frame records and native CLI outcomes, no private reads."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import sys

number = sys.argv[1] if len(sys.argv) == 2 else '076'
assert number in ['075', '076']
root = Path(__file__).resolve().parents[1] / ('reports/commercial61-native-' + number)
raw = root / 'runtime-evidence/raw'
manifest = json.loads((raw.parent / 'retrieval-manifest.json').read_text())
for name, item in manifest['files'].items():
    data = (raw / name).read_bytes()
    assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256']
requests = []
trace = raw / 'snapshot075-native-allocator-073.trace'
if trace.exists():
    for line in trace.read_text().splitlines():
        match = re.fullmatch(r'COMMERCIAL073_ALLOC_REQUEST sequence=(\d+) pid=(\d+) uid=(\d+) width=(\d+) height=(\d+) format=(-?\d+) usage=(0x[0-9a-f]+) expected=(\d+) public_interface=1', line)
        assert match, 'Malformed own allocator snapshot line'
        values = match.groups()
        row = dict(zip(['sequence','pid','uid','width','height','format','usage','expected'],
            [int(v,16) if i == 6 else int(v) for i,v in enumerate(values)]))
        assert row['uid'] == 3041
        row['usage_hex'] = hex(row['usage'])
        requests.append(row)
    assert len(requests) <= 128 and len({r['sequence'] for r in requests}) == len(requests)
perf = raw / 'snapshot075-native-perf-023.trace'
frames = []
if perf.exists():
    for line in perf.read_bytes().splitlines():
        if line.startswith(b'COMMERCIAL030_FRAME '):
            fields = {key.decode():int(value) for key,value in re.findall(rb'(\w+)=(-?\d+)',line)}
            if set(fields) >= {'sequence','mono_us','output_valid','source_nonblack','output_nonblack'}:
                frames.append(fields)
hilog = (raw / 'interactive-hilog030.log').read_text(errors='replace').splitlines()
categories = {
    'guide_stop_requests': ['Kill process, bundleName: com.huawei.hmos.hwstartupguide'],
    'permission_failures': ['KillProcess permission verification fail', 'caller invalid'],
    'codec_buffer_allocation_failures': ['Start codec failed: cannot allocate buffers'],
    'codec_sendframe_failures': ['decode frame error: ret = -1'],
    'scene_first_flush': ['com.ohos.sceneboard/Ace', 'ArkUi flush first frame messages.'],
}
messages = {key:[line for line in hilog if (all(token in line for token in tokens) if key == 'scene_first_flush'
                                          else any(token in line for token in tokens))]
            for key,tokens in categories.items()}
last = next((line for line in reversed(hilog) if re.match(r'\d\d-\d\d \d\d:',line)), None)
groups = Counter((r['width'],r['height'],r['format'],r['usage_hex']) for r in requests)
result = dict(run=manifest['run'], verified_files=len(manifest['files']), public_requests=requests,
    request_groups=[dict(width=w,height=h,format=f,usage_hex=u,count=n) for (w,h,f,u),n in groups.items()],
    request_log_limit=128, request_log_saturated=len(requests)==128, request_returns_not_observed=True,
    prefix_trace_not_eof=True, recovered_frame_records=frames,
    messages=messages, message_counts={k:len(v) for k,v in messages.items()}, last_hilog_line=last,
    no_private_process_memory_read=True, desktop_verified=False, interaction_verified=False, activation_verified=False)
(root / 'public-outcome-analysis.json').open('x').write(json.dumps(result,indent=2))
print(json.dumps(dict(run=result['run'], request_groups=result['request_groups'],
    request_log_saturated=result['request_log_saturated'], frame_records=len(frames),
    message_counts=result['message_counts'], last_hilog_line=last),indent=2))
