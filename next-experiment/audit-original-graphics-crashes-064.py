"""Recover the disposable guest scratch on a fresh clone; preserve all source evidence."""
import subprocess

payload = r'''
from pathlib import Path
import hashlib,json,re,shutil,subprocess
project=Path('/mnt/d/lab/HarmonyOSForMatebookego')
record=json.loads((project/'reports/baremetal-sdk-original-init-qemu-064/result.json').read_text())
scratch=record['scratch_data']
assert scratch['ram_backed'] and scratch['freshly_formatted'] and not scratch['original_userdata_attached']
original=Path(scratch['retained_path'])
assert original.parent.name=='baremetal-sdk-original-init-qemu-064' and original.name=='scratch-data.ext4'
expected=scratch['after_sha256']
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as stream:
  for block in iter(lambda:stream.read(4*1024*1024),b''):h.update(block)
 return h.hexdigest()
assert original.stat().st_size==scratch['bytes'] and sha(original)==expected
out=project/'reports/original-graphics-crashes-064'
work=Path('/home/zoinve/harmony-virgl-883/original-graphics-crashes-064')
assert not out.exists() and not work.exists()
out.mkdir();work.mkdir()
recovered=work/'scratch-recovery-copy.ext4'
with original.open('rb') as source, recovered.open('xb') as destination:
 shutil.copyfileobj(source,destination,4*1024*1024)
assert sha(recovered)==expected
fsck_command=['e2fsck','-f','-p',str(recovered)]
check=subprocess.run(fsck_command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=90)
(out/'recovery.stdout').write_bytes(check.stdout);(out/'recovery.stderr').write_bytes(check.stderr)
recovery=dict(command=fsck_command,returncode=check.returncode,original_sha256=expected,
 recovery_copy_sha256=sha(recovered),original_unchanged=sha(original)==expected,
 source_kind='disposable guest scratch clone, not original SDK or user data')
(out/'recovery.json').write_text(json.dumps(recovery,indent=2))
assert check.returncode in (0,1) and recovery['original_unchanged'],recovery
listing=subprocess.run(['debugfs','-R','ls -l /log/faultlog/faultlogger',str(recovered)],
 stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=20)
(out/'listing.stdout').write_bytes(listing.stdout);(out/'listing.stderr').write_bytes(listing.stderr)
assert listing.returncode==0
assert not any(word in listing.stderr.lower() for word in (b'checksum',b'not found',b'not open',b'bad magic'))
names=sorted(set(re.findall(rb'cppcrash-render_service-[A-Za-z0-9_.-]+',listing.stdout)))
logs=[]
for encoded in names:
 name=encoded.decode();assert Path(name).name==name
 dump=subprocess.run(['debugfs','-R','cat /log/faultlog/faultlogger/'+name,str(recovered)],
  stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=20)
 assert dump.returncode==0 and dump.stdout
 (out/name).write_bytes(dump.stdout);(out/(name+'.stderr')).write_bytes(dump.stderr)
 text=dump.stdout.decode(errors='replace')
 logs.append(dict(name=name,bytes=len(dump.stdout),sha256=hashlib.sha256(dump.stdout).hexdigest(),
  header=text[:2500],recovered_view=True))
assert sha(original)==expected
result=dict(recovery=recovery,logs=logs,original_scratch_unchanged=True,
 original_sdk_images_accessed=False,vm_rerun=False,desktop_verified=False)
(out/'result.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
'''
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],
                                   input=payload,text=True,timeout=180).returncode)
