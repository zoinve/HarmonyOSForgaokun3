"""Read-only, hash-recorded disassembly around the actual original RS crash PC."""
from pathlib import Path
import subprocess

payload = r'''
from pathlib import Path
import hashlib,json,subprocess
project=Path('/mnt/d/lab/HarmonyOSForMatebookego')
root=Path('/home/zoinve/harmony-virgl-883')
out=project/'reports/original-render-fault-054'
work=root/'original-render-fault-054'
assert not out.exists() and not work.exists()
result=json.loads((project/'reports/baremetal-sdk-original-init-qemu-054/result.json').read_text())
image=Path(result['original_images']['system.img']['path'])
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
before=sha(image)
assert before==result['original_images']['system.img']['sha256']
out.mkdir();work.mkdir()
elf=work/'librender_service.z.so'
p=subprocess.run(['debugfs','-R','dump /system/lib64/librender_service.z.so '+str(elf),str(image)],capture_output=True,check=True)
(out/'extract.stderr').write_bytes(p.stderr)
assert elf.read_bytes()[:5]==b'\x7fELF\x02'
commands=[['llvm-readelf-19','-nW',str(elf)],
 ['llvm-objdump-19','-dC','--start-address=0x40f25c','--stop-address=0x40f520',str(elf)]]
files=[]
for i,cmd in enumerate(commands):
 p=subprocess.run(cmd,capture_output=True,check=True)
 for suffix,body in [('stdout',p.stdout),('stderr',p.stderr)]:
  name=str(i)+'.'+suffix+'.txt';(out/name).write_bytes(body)
  files.append(dict(path=name,bytes=len(body),sha256=hashlib.sha256(body).hexdigest()))
assert b'2ceb723e313c80c3605ecd369c0b8cb6' in (out/'0.stdout.txt').read_bytes()
assert sha(image)==before
evidence=dict(original_system_unchanged=True,target_code_executed=False,rs_elf_path=str(elf),rs_elf_sha256=sha(elf),files=files)
(out/'result.json').write_text(json.dumps(evidence,indent=2))
print(json.dumps(evidence,indent=2))
'''
compile(payload, 'original-rs-fault-054-audit', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
