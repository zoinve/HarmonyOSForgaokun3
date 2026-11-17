"""Analyze the completed minimal commercial attempt without inferring a desktop."""
from pathlib import Path
import hashlib,json,re
root=Path(__file__).resolve().parents[1]/'reports/commercial61-native-002'
raw=root/'runtime-evidence/raw'
phase=max(raw.glob('phase-*.log'),key=lambda p:int(p.stem.split('-')[-1]))
text=phase.read_text(errors='replace')
observations=[(int(s),int(p),c.strip()) for s,p,c in re.findall(r'COMMERCIAL001_PROCESS sample=(\d+) pid=(\d+) cmd=([^\n]*)',text) if int(s)>0]
rs={(s,p,c) for s,p,c in observations if c=='/system/bin/render_service'}
commands=sorted({c for _,_,c in observations})
hilog=(raw/'interactive-hilog030.log').read_text(errors='replace')
result=dict(last_phase=phase.name,phase_sha256=hashlib.sha256(phase.read_bytes()).hexdigest(),
 original_init_observed=any(p==1 and c.startswith('/system/bin/init') for _,p,c in observations),
 original_render_service_observations=[dict(sample=s,pid=p,command=c) for s,p,c in sorted(rs)],
 render_service_unique_pids=sorted({p for _,p,_ in rs}),
 hdf_devmgr_observed=any(re.search(r'(^|/)hdf_devmgr(?: |$)',c) for c in commands),
 scene_board_observed=any('sceneboard' in c.lower() for c in commands),
 hdf_missing_sa_lines=sum('GetSaWrap' in line and ('5100' in line or 'not start' in line) for line in hilog.splitlines()),
 target_timeout='COMMERCIAL002 target_timeout=1' in text,
 sdk_userland_used=False,original_commercial_images_unchanged_by_design=True,
 diagnostic_limitation='The 002 diagnostic helpers used fd 199 after the collector closed it. Early kmsg and redirected RenderService logs are incomplete; 003 corrects descriptor ownership only.',
 exact_hdf_failure_cause_established=False,desktop_verified=False,physical_input_verified=False,
 evidence_limit='A sampled process with a stable PID proves execution, not correct rendering, service readiness or an interactive desktop.')
dest=root/'minimal-startup-analysis.json';dest.open('x').write(json.dumps(result,indent=2))
print(json.dumps({k:v for k,v in result.items() if k!='original_render_service_observations'},indent=2))
