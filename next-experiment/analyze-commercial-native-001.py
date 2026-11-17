"""Conservative boot-layer analysis from immutable captured evidence, not UI claims."""
from pathlib import Path
import hashlib,json,re
root=Path(__file__).resolve().parents[1]/'reports/commercial61-native-001'
raw=root/'runtime-evidence/raw';assert raw.is_dir()
phases=sorted(raw.glob('phase-*.log'),key=lambda p:int(p.stem.split('-')[-1]));assert phases
phase=phases[-1];text=phase.read_text(errors='replace')
processes={}
for sample,pid,cmd in re.findall(r'COMMERCIAL001_PROCESS sample=(\d+) pid=(\d+) cmd=([^\n]*)',text):
 if int(sample)>0:processes.setdefault(cmd.strip(),set()).add(int(pid))
pid1=[cmd for cmd,ids in processes.items() if 1 in ids]
init_observed=any('/system/bin/init' in cmd for cmd in pid1)
hilog=raw/'interactive-hilog030.log';logs=hilog.read_text(errors='replace') if hilog.exists() else ''
failure_lines=[]
for line in (text+'\n'+logs).splitlines():
 if re.search(r'COMMERCIAL.*FAIL|NATIVE_ORIGINAL001_FAIL|CANNOT LINK|Error loading shared|Exec.*failed|exec.*fail|FATAL',line):
  if line not in failure_lines:failure_lines.append(line)
service_processes={k:sorted(v) for k,v in processes.items() if '/system/bin/' in k or '/vendor/bin/' in k}
result=dict(last_phase=phase.name,last_phase_sha256=hashlib.sha256(phase.read_bytes()).hexdigest(),
 original_commercial_handoff_logged='COMMERCIAL001_HANDOFF original_commercial_init=1' in text,
 original_commercial_init_observed_after_exec=init_observed,pid1_commands=pid1,
 observed_original_service_commands=service_processes,unique_original_command_count=len(service_processes),
 target_exit_records=re.findall(r'COMMERCIAL001_TARGET_EXIT[^\n]*',text),
 timeout_records=re.findall(r'COMMERCIAL001 target_timeout[^\n]*',text),
 fault_or_exec_evidence=failure_lines[:80],hilog_bytes=hilog.stat().st_size if hilog.exists() else 0,
 sdk_userland_used=False,desktop_verified=False,physical_input_verified=False,
 commercial_image_metadata='6.0.0.110 API 20',
 evidence_limit='Process observations prove execution only, not service health, successful rendering or desktop usability.')
(root/'runtime-analysis.json').open('x').write(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
