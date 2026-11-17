"""Hash-verified proc maps and execution-breakpoint registers, no object reads."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re

root=Path(__file__).resolve().parents[1]/'reports/commercial61-native-071'
raw=root/'runtime-evidence/raw'
manifest=json.loads((raw.parent/'retrieval-manifest.json').read_text())
for name,item in manifest['files'].items():
    data=(raw/name).read_bytes()
    assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256']
phase=max(raw.glob('phase-*.log'),key=lambda p:int(p.stem.split('-')[1]))
text=phase.read_text(errors='replace')
rows=[]
for line in text.splitlines():
    if line.startswith('COMMERCIAL071_CODEC_HW_'):
        row=dict(re.findall(r'(\w+)=([^\s]+)',line))
        row['kind']=line.split()[0].removeprefix('COMMERCIAL071_CODEC_HW_')
        if row['kind']=='SAMPLE':
            value=int(row['x0'],16)&0xffffffff
            row['x0_i32']=value-(1<<32) if value&(1<<31) else value
        rows.append(row)
samples=[r for r in rows if r['kind']=='SAMPLE']
counts=[r for r in rows if r['kind']=='COUNTS']
errors=[r for r in rows if any(k in r['kind'] for k in ['FAILED','BAD_','REFUSED','LIMIT'])]
blob=(raw/'interactive-faults030.log').read_bytes()
pattern=(rb'COMMERCIAL043_STREAM_BEGIN sample=(\d+) pid=(\d+) path=(/proc/\d+/maps) limit=(\d+)\n'
    rb'(.*?)\nCOMMERCIAL043_STREAM_END sample=\1 pid=\2 path=\3 bytes=(\d+) eof=(\d+) errno=(\d+)')
inventories=[]
for match in re.finditer(pattern,blob,re.S):
    body=match[5]
    assert len(body)==int(match[6]) and len(body)<=int(match[4])
    if not any(k in body for k in [b'libfcodec.z.so',b'libhevc_decoder.z.so',b'libhevcdec_ohos.z.so']):
        continue
    inventories.append(dict(sample=int(match[1]),pid=int(match[2]),bytes=len(body),
        eof=int(match[7]),errno=int(match[8]),sha256=hashlib.sha256(body).hexdigest(),
        lines=[line for line in body.decode(errors='replace').splitlines() if any(k in line for k in [
            'libfcodec.z.so','libhevc_decoder.z.so','libhevcdec_ohos.z.so','libl410ffmpeg.z.so','libohosffmpeg.z.so'])]))
events={name:dict(samples=len(selected),x0_i32=dict(Counter(str(r['x0_i32']) for r in selected)),
    first_seconds=min(int(r['ns'])/1e9 for r in selected),last_seconds=max(int(r['ns'])/1e9 for r in selected))
    for name in sorted({r['event'] for r in samples}) for selected in [[r for r in samples if r['event']==name]]}
result=dict(run=manifest['run'],verified_files=len(manifest['files']),source_phase=phase.name,
    events=events,attachment_count=sum(r['kind']=='ATTACHED' for r in rows),errors=errors,
    instruction_pointer_mismatches=sum(r.get('ip_matches')!='1' for r in samples),
    max_reported_lost=max([int(r['lost']) for r in counts] or [0]),
    max_reported_malformed=max([int(r['malformed']) for r in counts] or [0]),
    stopped=any(r['kind']=='STOPPED' for r in rows),
    normal_target_timeout='COMMERCIAL071 target_timeout=1' in text,
    codec_inventories=inventories,rows=rows,
    absence_is_not_nonexecution_proof=True,live_private_object_reads=False,
    original_service_instruction_replacement=False,desktop_verified=False,interaction_verified=False)
with (root/'codec-analysis.json').open('x') as out:
    json.dump(result,out,indent=2)
print(json.dumps({k:v for k,v in result.items() if k not in ['rows','codec_inventories','errors']},indent=2))
print(json.dumps(dict(errors=errors[:8],codec_inventories=inventories[:2]),indent=2))
