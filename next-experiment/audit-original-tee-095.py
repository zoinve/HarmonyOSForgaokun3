"""Compare original client device expectations with host kernel metadata only."""
from pathlib import Path
import hashlib
import json
import re
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
IMAGE = '/mnt/c/Users/39255/AppData/Local/Temp/opencode/qemu-desktop-images-092/p111-system.kr990-ext4-v1.img'

REMOTE = r'''
from pathlib import Path
import gzip,json,os,re,stat
records=[]
for path in sorted(Path('/boot').glob('config-*gaokun3*')):
 text=path.read_text()
 records.append(dict(path=str(path),lines=[line for line in text.splitlines() if re.match(r'^(?:# )?CONFIG_(?:TEE|OPTEE|TC_NS|TZDRIVER|TRUSTZONE|QCOM_QSEECOM|QCOM_SCM|QCOM_TZMEM)(?:_|=| )',line)]))
nodes=[]
for pattern in ('tee*','tc_ns*','tz*','qsee*'):
 for path in Path('/dev').glob(pattern):
  s=path.lstat()
  nodes.append(dict(path=str(path),character=stat.S_ISCHR(s.st_mode),major=os.major(s.st_rdev),minor=os.minor(s.st_rdev)))
drivers=[]
for base in ('/sys/bus/platform/drivers','/sys/bus/auxiliary/drivers'):
 for path in Path(base).iterdir():
  if re.search(r'tee|qsee|tzdriver',path.name,re.I):drivers.append(str(path))
print(json.dumps(dict(kernel=os.uname().release,configs=records,device_metadata=nodes,drivers=drivers,
 trust_firmware_called=False,device_nodes_opened=False,security_storage_read=False)))
'''

if __name__ == '__main__':
    out = ROOT / 'reports/original-tee-interface-095.json'
    assert not out.exists()
    binaries=[]
    for path in ('/system/bin/teecd', '/system/lib64/chipset-sdk-sp/libteec_vendor.so'):
        process=subprocess.run(['debugfs','-R','cat '+path,IMAGE],capture_output=True,check=True)
        body=process.stdout
        assert body.startswith(b'\x7fELF'),path
        strings=re.findall(rb'[\x20-\x7e]{5,}',body)
        paths=sorted(set(s.decode() for s in strings if s.startswith(b'/dev/') or
                         (s.startswith(b'/') and (b'teec' in s or b'cadaemon' in s))))
        binaries.append(dict(path=path,bytes=len(body),sha256=hashlib.sha256(body).hexdigest(),
                             relevant_literal_paths=paths))
    workflow=runpy.run_path(str(BASE/'commercial-workflow-094.py'))
    workflow['configure_local_transport']()
    result=subprocess.run(['ssh','matebook','python3 -'],input=REMOTE,text=True,
                          capture_output=True,timeout=40)
    assert result.returncode==0,result.stderr
    record=dict(original_clients=binaries,host_metadata=json.loads(result.stdout),
                original_images_written=False,target_booted=False,
                device_alias_or_replacement_created=False,firmware_or_certificates_modified=False)
    out.open('x').write(json.dumps(record,indent=2))
    print(json.dumps(record,indent=2))
