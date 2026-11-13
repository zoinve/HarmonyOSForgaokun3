"""Copy existing board firmware to a fresh lab directory; never load or install it."""
from pathlib import Path
import json
import subprocess

report = Path(__file__).resolve().parent.parent / 'reports/baremetal-firmware-staged-001.json'
assert not report.exists()
payload = r'''
from pathlib import Path
import hashlib,json,shutil,subprocess
work=Path('/mnt/harmony-lab/work')
assert subprocess.check_output(['findmnt','-n','-o','SOURCE','--target',str(work)],text=True).strip()=='/dev/nvme0n1p4'
assert subprocess.check_output(['findmnt','-n','-o','UUID','--target',str(work)],text=True).strip()=='00029cdd-1748-4d2f-b73b-8e8164922098'
dest=work/'firmware-baseline-001';assert not dest.exists()
source=Path('/lib/firmware')
board=source/'qcom/sc8280xp/HUAWEI/gaokun3'
files=sorted(p for p in board.rglob('*') if p.is_file())
assert len(files)==10
files += [source/'qcom/a660_sqe.fw',source/'qcom/a660_gmu.bin']
assert all(p.is_file() for p in files)
dt=Path('/sys/firmware/devicetree/base')
required=[]
for p in dt.rglob('firmware-name'):
 for name in p.read_bytes().split(b'\0'):
  if name:required.append(name.decode())
assert len(required)==5 and all(source/name in files for name in required)
def sha(p):
 with p.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
before={str(p):sha(p) for p in files}
dest.mkdir();rows=[]
for p in files:
 name=p.relative_to(source);target=dest/'lib/firmware'/name
 target.parent.mkdir(parents=True,exist_ok=True)
 shutil.copyfile(p,target);target.chmod(0o444)
 assert sha(target)==before[str(p)] and target.stat().st_size==p.stat().st_size
 rows.append(dict(name=name.as_posix(),bytes=target.stat().st_size,sha256=before[str(p)]))
assert all(sha(p)==before[str(p)] for p in files)
result=dict(destination=str(dest),files=rows,files_verified=len(rows),
 device_tree_required_firmware=sorted(required),source_firmware_unchanged=True,
 installed_to_host=False,firmware_loaded=False,boot_entries_modified=False,native_boot_attempted=False,
 scope='board firmware and Adreno 690 microcode only; not a complete Wi-Fi or initramfs firmware closure')
(dest/'manifest.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
'''
compile(payload, 'stage-existing-board-firmware', 'exec')
r = subprocess.run(['ssh', 'matebook', 'python3 -'], input=payload,
                   text=True, capture_output=True, check=True, timeout=180)
result = json.loads(r.stdout)
assert result['files_verified'] == 12 and result['source_firmware_unchanged']
report.write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps({k: result[k] for k in ['destination', 'files_verified', 'source_firmware_unchanged',
                                      'installed_to_host', 'native_boot_attempted']}, indent=2))
