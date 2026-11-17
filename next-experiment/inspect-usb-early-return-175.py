"""Inspect a known early-return run without exporting raw kernel/USB strings."""
from pathlib import Path
import json
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
REPORT = BASE.parent / 'reports/commercial61-native-175-compile-fix-1'
PAYLOAD = r'''
from pathlib import Path
import hashlib,json,re,subprocess
mount=Path('/mnt/usb-early-inspection-175')
assert not mount.exists()
assert not subprocess.run(['findmnt','-rn','-S','/dev/nvme0n1p4'],capture_output=True,text=True).stdout.strip()
mount.mkdir(mode=0o700)
mounted=False
try:
 subprocess.run(['mount','-t','ext4','-o','ro,noload,nodev,nosuid,noexec','/dev/nvme0n1p4',str(mount)],check=True,timeout=30)
 mounted=True
 runs=list(mount.glob('commercial61-native-087-d8e6833f-db76-4669-acad-51db7b57cc6e'))
 assert len(runs)==1
 run=runs[0]
 phases=sorted([path for path in run.iterdir() if re.fullmatch(r'phase-\d+\.log',path.name)],key=lambda path:int(path.stem[6:]))
 assert phases and all(path.is_file() and not path.is_symlink() for path in phases)
 text=phases[-1].read_text(errors='replace')
 modules=[dict(kind=kind,module=module,status=int(status) if status else None) for kind,module,status in
  re.findall(r'^INPUTUSB148_MODULE_(PRESENT|RESULT) module=(\w+)(?: status=(-?\d+))? storage_acceptance_not_inferred=1$',text,re.M)]
 reasons=re.findall(r'^USB175_REFUSED reason=([a-z_]+)$',text,re.M)
 result=dict(run=run.name,latest_phase=phases[-1].name,
  phase_files={path.name:dict(bytes=path.stat().st_size,sha256=hashlib.sha256(path.read_bytes()).hexdigest()) for path in phases},
  guard_refusal_reasons=reasons,protection_marker_seen=bool(re.search(r'^USB175_PROTECTED ',text,re.M)),
  native_original_start_seen=bool(re.search(r'^NATIVE_ORIGINAL_START ',text,re.M)),
  original_init_handoff_seen='COMMERCIAL001_HANDOFF' in text,
  persistent_prepare_marker_seen='PERSISTENT166_' in text,
  expected_readonly_optin_seen='harmony.usb_readonly175=1' in text,
  storage_module_results=modules,
  usb_numeric_ids=[dict(vid=vid,pid=pid) for vid,pid in sorted(set(re.findall(r'idVendor=([0-9a-fA-F]{4}), idProduct=([0-9a-fA-F]{4})',text)))],
  kernel_scsi_disk_attach_message_seen=bool(re.search(r'\bsd \d+:\d+:\d+:\d+: \[sd[a-z]+\]',text)),
  sd_mod_module_line_seen=bool(re.search(r'^sd_mod \d+ ',text,re.M)),
  raw_logs_exported=False,usb_serials_exported=False,source_readonly_noload=True,
  expected_snapshot_missing=not (run/'snapshot075-commercial-desktop086.log').exists())
finally:
 if mounted:subprocess.run(['umount',str(mount)],check=True,timeout=30)
 mount.rmdir()
result['lab_partition_unmounted']=True
print(json.dumps(result,indent=2))
'''


if __name__ == '__main__':
    output = REPORT / 'early-return-inspection.json'
    assert not output.exists()
    runpy.run_path(str(BASE / 'commercial-workflow-175.py'))['configure_local_transport']()
    proc = subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',
        '-o','HostName=192.168.10.128','-o','HostKeyAlias=192.168.10.128','matebook','sudo -n python3 -'],
        input=PAYLOAD,text=True,capture_output=True,timeout=90)
    (REPORT / 'early-return-inspection.stderr').open('x').write(proc.stderr)
    assert proc.returncode==0,proc.stderr
    data=json.loads(proc.stdout)
    output.open('x').write(json.dumps(data,indent=2))
    print(json.dumps(data,indent=2))
