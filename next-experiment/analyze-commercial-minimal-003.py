"""Preserve exact loader/kernel/renderer diagnostics from the third bounded run."""
from pathlib import Path
import hashlib,json,re
root=Path(__file__).resolve().parents[1]/'reports/commercial61-native-003'
raw=root/'runtime-evidence/raw'
phase=max(raw.glob('phase-*.log'),key=lambda p:int(p.stem.split('-')[-1]))
phase_text=phase.read_text(errors='replace')
fault=raw/'interactive-faults030.log';diagnostics=fault.read_text(errors='replace')
observations=set(re.findall(r'COMMERCIAL001_PROCESS sample=(\d+) pid=(\d+) cmd=([^\n]*)',phase_text))
commands=sorted({c.strip() for s,_,c in observations if int(s)>0})
selected=[]
for number,line in enumerate(diagnostics.splitlines(),1):
 if re.search(r'COMMERCIAL002_(COMMAND|KMSG_OPEN|RS_LOG)|Error loading|Error relocating|hdf_devmgr|render_service|[Ff]ailed to (start|exec)|[Ss]ervice.*(fail|exit)|[Cc]annot link',line):
  selected.append(f'{number}: {line}')
(root/'diagnostic-context.txt').open('x',encoding='utf-8').write('\n'.join(selected))
result=dict(last_phase=phase.name,phase_sha256=hashlib.sha256(phase.read_bytes()).hexdigest(),
 diagnostics_sha256=hashlib.sha256(fault.read_bytes()).hexdigest(),
 retained_command_results=re.findall(r'COMMERCIAL002_COMMAND[^\n]*',diagnostics),
 early_kernel_records=diagnostics.count('COMMERCIAL002_KMSG '),
 render_log_snapshots=diagnostics.count('COMMERCIAL002_RS_LOG'),
 observed_commands=commands,
 original_init_observed=any(int(p)==1 and c.startswith('/system/bin/init') for s,p,c in observations if int(s)>0),
 render_service_pids=sorted({int(p) for s,p,c in observations if int(s)>0 and c.strip()=='/system/bin/render_service'}),
 hdf_devmgr_observed=any(re.search(r'(^|/)hdf_devmgr(?: |$)',c) for c in commands),
 source_images='ISO-verified commercial61-original-001; no SDK substitution',
 service_change_from_002=False,desktop_verified=False,physical_input_verified=False,
 limitation='Process observations and diagnostic errors need root-cause interpretation; they do not prove service health or a usable desktop.')
(root/'minimal-startup-analysis.json').open('x').write(json.dumps(result,indent=2))
print(json.dumps({k:v for k,v in result.items() if k!='observed_commands'},indent=2))
