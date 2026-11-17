"""Retain observed path/mount facts without treating root reads as app access."""
from pathlib import Path
import hashlib
import json
import re

root = Path(__file__).resolve().parents[1] / 'reports/commercial61-native-069'
raw = root / 'runtime-evidence/raw'
manifest = json.loads((raw.parent / 'retrieval-manifest.json').read_text())
for name, item in manifest['files'].items():
    data = (raw / name).read_bytes()
    assert len(data) == item['bytes'] and hashlib.sha256(data).hexdigest() == item['sha256']
blob = (raw / 'interactive-faults030.log').read_bytes()
rows = []
for line in blob.decode(errors='replace').splitlines():
    if not line.startswith(('COMMERCIAL069_RESOURCE_STAT ', 'COMMERCIAL069_RESOURCE_ENTRY ',
                            'COMMERCIAL069_RESOURCE_PREFIX ')):
        continue
    values = dict(re.findall(r'(\w+)=([^\s]+)',line))
    values['kind'] = line.split()[0].removeprefix('COMMERCIAL069_RESOURCE_')
    rows.append(values)
stats = [r for r in rows if r['kind']=='STAT']
mounts = []
pattern = (rb'COMMERCIAL043_STREAM_BEGIN sample=(\d+) pid=(\d+) path=(/proc/\d+/mountinfo) limit=(\d+)\n'
           rb'(.*?)\nCOMMERCIAL043_STREAM_END sample=\1 pid=\2 path=\3 bytes=(\d+) eof=(\d+) errno=(\d+)')
for match in re.finditer(pattern,blob,re.S):
    body = match[5]
    assert len(body)==int(match[6]) and len(body)<=int(match[4])
    mounts.append(dict(sample=int(match[1]),pid=int(match[2]),path=match[3].decode(),
        bytes=len(body),eof=int(match[7]),errno=int(match[8]),
        relevant_lines=[line for line in body.decode(errors='replace').splitlines()
            if any(p in line for p in ['/data/storage/el1/bundle',
                '/system/app/HwStartupGuide','/data/app/el1/bundle/public/com.huawei.hmos.hwstartupguide'])]))
videos = [r for r in stats if r['path'].endswith(('.mp4'))]
hap = [r for r in stats if r['path']=='/system/app/HwStartupGuide/HwStartupGuide.hap']
indices = [r for r in stats if r['path'].endswith('/resources.index')]
result = dict(run=manifest['run'],verified_files=len(manifest['files']),
    observed_pids=sorted({int(r['pid']) for r in stats}),
    observed_samples=sorted({int(r['sample']) for r in stats}),
    stat_records=len(stats),preinstall_hap_successful_stats=sum(r['stat']=='0' for r in hap),
    video_successful_stats=sum(r['stat']=='0' for r in videos),video_total_stats=len(videos),
    extracted_index_successful_stats=sum(r['stat']=='0' for r in indices),
    extracted_index_total_stats=len(indices),records=rows,mounts=mounts,
    root_read_does_not_prove_original_app_read_permission=True,
    missing_paths_not_alone_proof_of_required_repair=True,
    desktop_verified=False,interaction_verified=False)
with (root/'resource-inventory-analysis.json').open('x') as out:
    json.dump(result,out,indent=2)
print(json.dumps({k:v for k,v in result.items() if k not in ('records','mounts')},indent=2))
