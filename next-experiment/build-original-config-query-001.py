"""Compile-only original public C API diagnostic; never execute target ELF here."""
import subprocess

payload = r'''
from pathlib import Path
import hashlib,json,subprocess
project=Path('/mnt/d/lab/HarmonyOSForMatebookego')
root=Path('/home/zoinve/harmony-virgl-883')
work=root/'original-config-query-001'
report=project/'reports/original-config-query-001'
assert not work.exists() and not report.exists()
work.mkdir();report.mkdir()
source=project/'next-experiment/original-config-query-001.c'
body=source.read_bytes(); (work/'query.c').write_bytes(body)
cmd=[str(root/'window-bridge/toolchain/ohos-cc'),'-O2','-Wall','-Wextra','-Werror',str(work/'query.c'),'-ldl','-o',str(work/'query')]
p=subprocess.run(cmd,capture_output=True)
(report/'compile.stdout').write_bytes(p.stdout);(report/'compile.stderr').write_bytes(p.stderr)
assert p.returncode==0,p.stderr.decode(errors='replace')
elf=(work/'query').read_bytes()
assert elf[:6]==b'\x7fELF\x02\x01' and elf[18:20]==b'\xb7\0'
dynamic=subprocess.check_output(['readelf','-dW',str(work/'query')],text=True)
(report/'dynamic.txt').write_text(dynamic)
assert 'libc.so.6' not in dynamic and 'libstdc++' not in dynamic
result=dict(path=str(work/'query'),bytes=len(elf),sha256=hashlib.sha256(elf).hexdigest(),source_sha256=hashlib.sha256(body).hexdigest(),command=cmd,target_code_executed=False,diagnostic_caller_not_samgr=True)
assert source.read_bytes()==body
for dest in [report/'result.json',work/'result.json']:
 with dest.open('x') as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
'''
compile(payload, 'config-query-build', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180).returncode)
