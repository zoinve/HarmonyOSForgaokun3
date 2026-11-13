"""Recover original local BMS symbols from its compressed debug ELF, without execution."""
import subprocess

payload = r'''
from pathlib import Path
import hashlib,json,lzma,struct,subprocess
project=Path('/mnt/d/lab/HarmonyOSForMatebookego')
elf=Path('/home/zoinve/harmony-virgl-883/original-bms-paths-001/libbms.z.so')
body=elf.read_bytes()
expected='36fcf01ce7079acf0ba68aa2e08368fb3aaba418325be6d6f6b62988aa903627'
assert hashlib.sha256(body).hexdigest()==expected
shoff=struct.unpack_from('<Q',body,40)[0]
entsize,count,namesindex=struct.unpack_from('<HHH',body,58)
sections=[struct.unpack_from('<IIQQQQIIQQ',body,shoff+i*entsize) for i in range(count)]
names=sections[namesindex]
strings=body[names[4]:names[4]+names[5]]
debug=[s for s in sections if strings[s[0]:].split(b'\0',1)[0]==b'.gnu_debugdata']
assert len(debug)==1
section=debug[0]
mini=lzma.decompress(body[section[4]:section[4]+section[5]])
assert mini[:5]==b'\x7fELF\x02'
out=project/'reports/original-bms-startup-001'
out.mkdir(exist_ok=False)
path=out/'mini.elf'
with path.open('xb') as f:f.write(mini)
command=['llvm-nm-19','-anC',str(path)]
p=subprocess.run(command,capture_output=True,check=True)
files=[]
for name,data in [('symbols.txt',p.stdout),('symbols.stderr',p.stderr)]:
 with (out/name).open('xb') as f:f.write(data)
 files.append(dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
assert hashlib.sha256(elf.read_bytes()).hexdigest()==expected
result=dict(original_elf_sha256=expected,original_elf_unchanged=True,target_code_executed=False,
            mini_sha256=hashlib.sha256(mini).hexdigest(),files=files,command=command)
with (out/'result.json').open('x') as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
'''

if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=120).returncode)
