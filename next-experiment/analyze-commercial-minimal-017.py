"""Hash-checked original-service and real scanout evidence; no assumed desktop."""
from pathlib import Path
import hashlib,json,re,runpy
root=Path(__file__).resolve().parent.parent/'reports/commercial61-native-017'
e=root/'runtime-evidence';m=json.loads((e/'retrieval-manifest.json').read_text())
for name,item in m['files'].items():
    blob=(e/'raw'/name).read_bytes()
    assert len(blob)==item['bytes'] and hashlib.sha256(blob).hexdigest()==item['sha256'],name
phase=max((e/'raw').glob('phase-*.log'),key=lambda p:int(p.stem.split('-')[1]))
s=phase.read_text(errors='replace')
h=(e/'raw/interactive-hilog030.log').read_text(errors='replace')
f=(e/'raw/interactive-faults030.log').read_text(errors='replace')
decode=runpy.run_path(str(Path(__file__).with_name('commercial-scanout-017.py')))['decode']
captures=[]
for match in re.finditer(r'COMMERCIAL016_SCANOUT sample=(\d+) bytes=(\d+) hex=([0-9a-f]+)\nCOMMERCIAL016_SCANOUT_END sample=\1',f):
    sample,size,encoded=match.groups()
    try:
        result=decode(int(size),encoded);blob=result.pop('blob')
        name='scanout-sample-'+sample+'.ppm'
        with (root/name).open('xb') as out:out.write(blob)
        captures.append(dict(sample=int(sample),file=name,valid=True,**result))
    except ValueError as error:captures.append(dict(sample=int(sample),valid=False,error=str(error)))
markers=[l for l in s.splitlines() if any(x in l for x in ['COMMERCIAL017_RAM_ADMISSION','COMMERCIAL016_GRAPHICS','NATIVE_RAM_DATA016','COMMERCIAL017 target_timeout','COMMERCIAL017_TARGET_EXIT','NATIVE_ORIGINAL001_FAIL','NATIVE_ORIGINAL_END'])]
gpu=list(dict.fromkeys(l for l in (s+'\n'+f).splitlines() if any(x in l for x in ['NATIVE_GPU041','stage=composer_gpu_','gpu_scanout_ready041','gpu_scanout_fallback041'])))
processes=list(dict.fromkeys(l for l in s.splitlines() if 'COMMERCIAL001_PROCESS' in l and any(x in l.lower() for x in ['sceneboard','render_service','composer_host','allocator_host'])))
data=dict(run=m['run'],verified_files=len(m['files']),last_phase=phase.name,evidence=markers,
    configured_target_kill_observed='COMMERCIAL017 target_timeout=1' in s,
    sa511_unsupported=len(re.findall(r'LoadSystemAbility SA:511 not supported',h)),
    enospc_lines=sum(any(x in l.lower() for x in ['errno:28','errno=28','no space left','database or disk is full']) for l in h.splitlines()),
    sceneboard_install_succeeded=bool(re.search(r'finish install com\.ohos\.sceneboard resultCode: 0',h)),
    sceneboard_process_observed=any('sceneboard' in l.lower() for l in processes),
    process_evidence=processes,gpu_evidence=gpu,captures=captures,
    mali_context_failure='Failed creating base context during opening of kernel driver.' in f,
    sdk_userland_used=False,desktop_verified=False,physical_input_verified=False,
    original_partition_journal_replayed=False)
with (root/'runtime-analysis.json').open('x') as out:json.dump(data,out,indent=2)
print(json.dumps(data,indent=2))
