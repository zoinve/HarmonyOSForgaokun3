"""Preserve partial-run metadata and sanitized boot markers after user reboot."""
from pathlib import Path
import json
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
if __name__ == '__main__':
    out = ROOT/'reports/commercial61-native-094/interrupted-run-audit.json'
    assert not out.exists()
    excluded = [json.loads((ROOT/f'reports/commercial61-native-{number}/runtime-evidence/retrieval-manifest.json').read_text())['run']
                for number in ('087', '088', '089', '090', '091', '092')]
    code = 'excluded='+repr(excluded)+'\n'+r'''
from pathlib import Path
import hashlib,json,re,subprocess
mount=Path('/mnt/commercial-interrupted-audit-094');mount.mkdir(exist_ok=True)
assert subprocess.run(['findmnt','-rn','--source','/dev/nvme0n1p4'],capture_output=True).returncode!=0
subprocess.run(['mount','-t','ext4','-o','ro,noload,nodev,nosuid,noexec','/dev/nvme0n1p4',str(mount)],check=True)
try:
 runs=[p for p in mount.rglob('commercial61-native-087-*') if p.name not in excluded]
 assert len(runs)==1,[p.name for p in runs]
 run=runs[0]
 def sha(path):
  with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
 files={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in run.iterdir() if p.is_file()}
 phases=sorted(run.glob('phase-*.log'),key=lambda p:int(p.stem.split('-')[-1]))
 serials=[Path('/sys/class/dmi/id/'+key).read_bytes().strip() for key in ('product_serial','chassis_serial')]
 assert all(len(value)==16 and value.isalnum() for value in serials)
 private={value for serial in serials for value in (serial,serial.lower(),serial.upper())}
 lines=[]
 if phases:
  with phases[-1].open('rb') as stream:
   for line in stream:
    if len(line)>65536:continue
    if not re.search(rb'COMMERCIAL[0-9]+_|NATIVE_|EARLY093_|udidmodule|udid_static|udid_adp|GetDevUdid|SystemWriteParam',line):continue
    if re.search(rb'_PERF |PUBLIC_PIXEL|SCANOUT.*hex=|STREAM.*hex=',line):continue
    for value in private:line=line.replace(value,b'[PHYSICAL_SERIAL_REDACTED]')
    line=re.sub(rb'(?<![0-9a-fA-F])[0-9a-fA-F]{64}(?![0-9a-fA-F])',b'[HEX64_REDACTED]',line)
    text=line.decode('utf-8',errors='replace').replace('\x00','')
    if text not in lines:lines.append(text.rstrip())
 result=dict(run=run.name,files=files,selected_phase=phases[-1].name if phases else None,
  sanitized_status_lines=lines[:180],matching_status_lines=len(lines),
  original_raw_evidence_modified=False,original_partition_replayed=False,
  user_reported_oobe_reached_then_forced_reboot=True,automatic_return_not_proven=True,
  no_native_identity_or_desktop_success_inferred=True,physical_serial_values_exported=False,
  standalone_hex64_values_redacted=True)
 print(json.dumps(result))
finally:
 subprocess.run(['umount',str(mount)],check=True)
'''
    workflow = runpy.run_path(str(BASE/'commercial-workflow-094.py'))
    workflow['configure_local_transport']()
    process = subprocess.run(['ssh', 'matebook', 'sudo -n python3 -'], input=code, text=True,
        capture_output=True, timeout=180)
    assert process.returncode == 0, process.stderr
    result = json.loads(process.stdout)
    out.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
