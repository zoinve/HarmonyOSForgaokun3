"""Record observed original HDF execution separately from publication and desktop readiness."""
from pathlib import Path
import hashlib,json,re
root=Path(__file__).resolve().parents[1]/'reports/commercial61-native-004'
raw=root/'runtime-evidence/raw'
phase=max(raw.glob('phase-*.log'),key=lambda p:int(p.stem.split('-')[-1]))
text=phase.read_text(errors='replace')
diagnostics=(raw/'interactive-faults030.log').read_text(errors='replace')
hilog=(raw/'interactive-hilog030.log').read_text(errors='replace')
observations=set(re.findall(r'COMMERCIAL001_PROCESS sample=(\d+) pid=(\d+) cmd=([^\n]*)',text))
commands=sorted({c.strip() for s,_,c in observations if int(s)>0})
selected=[]
for source,contents in [('phase',text),('diagnostics',diagnostics),('hilog',hilog)]:
 for n,line in enumerate(contents.splitlines(),1):
  if re.search(r'COMMERCIAL004_BOARD|init.matebookego.cfg|hdf_devmgr|HDF.*[Ss]ervice[Mm]anager|[Pp]ublish.*5100|\[mali\]|Failed creating base context|Cfg error',line):
   selected.append(f'{source}:{n}: {line}')
(root/'board-hdf-context.txt').open('x',encoding='utf-8').write('\n'.join(selected))
result=dict(last_phase=phase.name,phase_sha256=hashlib.sha256(phase.read_bytes()).hexdigest(),
 board_overlay_applied='COMMERCIAL004_BOARD original_hdf_config_import=1' in text,
 original_init_observed=any(int(p)==1 and c.startswith('/system/bin/init') for s,p,c in observations if int(s)>0),
 hdf_devmgr_pids=sorted({int(p) for s,p,c in observations if int(s)>0 and c.strip()=='/vendor/bin/hdf_devmgr'}),
 render_service_pids=sorted({int(p) for s,p,c in observations if int(s)>0 and c.strip()=='/system/bin/render_service'}),
 observed_commands=commands,early_kernel_records=diagnostics.count('COMMERCIAL002_KMSG '),
 missing_matebook_config_error=bool(re.search(r'Cfg error[^\n]*init\.matebookego\.cfg[^\n]*not found',diagnostics)),
 hdf_publication_verified=False,desktop_verified=False,physical_input_verified=False,sdk_payload=False,
 limitation='Execution observations are not publication or health checks. Interpret original HDF logs before drawing a readiness conclusion.')
(root/'minimal-startup-analysis.json').open('x').write(json.dumps(result,indent=2))
print(json.dumps({k:v for k,v in result.items() if k!='observed_commands'},indent=2))
