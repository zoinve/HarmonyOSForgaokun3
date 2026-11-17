"""Read-only, hash-checked analysis of the completed single 010 boot."""
from pathlib import Path
import hashlib,json,re
root=Path(__file__).resolve().parent.parent/'reports/commercial61-native-010'
e=root/'runtime-evidence';manifest=json.loads((e/'retrieval-manifest.json').read_text())
for name,entry in manifest['files'].items():
    b=(e/'raw'/name).read_bytes()
    assert len(b)==entry['bytes'] and hashlib.sha256(b).hexdigest()==entry['sha256'],name
phase=max((e/'raw').glob('phase-*.log'),key=lambda p:int(p.stem.split('-')[1]))
s=phase.read_text(errors='replace');h=(e/'raw/interactive-hilog030.log').read_text(errors='replace')
f=(e/'raw/interactive-faults030.log').read_text(errors='replace')
markers=[l for l in s.splitlines() if any(x in l for x in ['COMMERCIAL010_RAM_ADMISSION','NATIVE_RAM_DATA016','COMMERCIAL010 target_timeout','COMMERCIAL010_TARGET_EXIT','NATIVE_ORIGINAL_END','COMMERCIAL010_STOPPED'])]
data=dict(run=manifest['run'],verified_files=len(manifest['files']),last_phase=phase.name,
    evidence=markers,configured_target_kill_observed='COMMERCIAL010 target_timeout=1' in s,
    stopped_cleanup_record_observed='COMMERCIAL010_STOPPED' in s,
    sa511_unsupported=len(re.findall(r'LoadSystemAbility SA:511 not supported',h)),
    enospc_lines=sum(any(x.lower() in l.lower() for x in ['errno:28','errno=28','No space left','database or disk is full']) for l in h.splitlines()),
    sceneboard_install_succeeded=bool(re.search(r'finish install com\.ohos\.sceneboard resultCode: 0',h)),
    mali_context_failure='Failed creating base context during opening of kernel driver.' in f,
    sdk_userland_used=False,desktop_verified=False,physical_input_verified=False,
    recovery_classification='Ubuntu observed online after configured guest termination; final cleanup outcome not captured',
    original_partition_journal_replayed=False)
assert data['configured_target_kill_observed'] and data['sceneboard_install_succeeded']
assert data['enospc_lines']==data['sa511_unsupported']==0 and data['mali_context_failure']
(root/'runtime-analysis.json').open('x').write(json.dumps(data,indent=2))
print(json.dumps(data,indent=2))
