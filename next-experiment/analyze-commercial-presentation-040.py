"""Derive presentation timing from original target records without synthesizing pixels."""
from pathlib import Path
import hashlib,json,re
root=Path(__file__).resolve().parents[1]/'reports/commercial61-native-040-r2'
raw=root/'runtime-evidence/raw'
h=(raw/'interactive-hilog030.log').read_text(errors='replace')
f=(raw/'interactive-faults030.log').read_text(errors='replace')
rows=list(dict.fromkeys(l for l in f.splitlines() if l.startswith('COMMERCIAL030_FRAME ')))
frames=[dict(re.findall(r'(\w+)=([^ ]+)',l)) for l in rows]
meta=[dict(re.findall(r'(\w+)=([^ ]+)',l)) for l in f.splitlines() if l.startswith('COMMERCIAL030_CAPTURE_META ')]
flush=[l for l in h.splitlines() if 'com.ohos.sceneboard/Ace' in l and 'ArkUi flush first frame messages.' in l]
flush_seconds=[]
for line in flush:
 m=re.search(r'01-01 (\d+):(\d+):(\d+\.\d+)',line)
 if m:flush_seconds.append((int(m[1])-8)*3600+int(m[2])*60+float(m[3]))
last=max((int(r['mono_us'])/1e6 for r in frames),default=None)
post=[r for r in frames if flush_seconds and int(r['mono_us'])/1e6>=flush_seconds[0]]
nonblack=[r for r in post if int(r['output_nonblack'])>0]
result=dict(sources={p.name:dict(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [raw/'interactive-hilog030.log',raw/'interactive-faults030.log']},frames=frames,captures=meta,sceneboard_first_flush=flush,first_flush_guest_seconds=flush_seconds,last_frame_seconds=last,postflush_frames=len(post),postflush_nonblack_sampled_frames=len(nonblack),actual_desktop_verified=False)
with (root/'presentation-analysis.json').open('x') as out:json.dump(result,out,indent=2)
print(json.dumps({k:result[k] for k in ['first_flush_guest_seconds','last_frame_seconds','postflush_frames','postflush_nonblack_sampled_frames','actual_desktop_verified']},indent=2))
