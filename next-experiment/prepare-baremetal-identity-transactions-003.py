"""Compile a fresh static transaction regression, without touching prior probes."""
from pathlib import Path
import json
import subprocess

base=Path(__file__).resolve().parent
source=(base/'baremetal-identity-ioctl-probe-002.c').read_text()
anchor='int main(void)'
assert source.count(anchor)==1
source=source.replace(anchor,(base/'baremetal-identity-transactions-003.h').read_text()+'\n'+anchor)
source=source.replace('    close(binder);close(fd);','    binder_transactions_003(binder,fd);\n    close(binder);close(fd);')
source=source.replace('IDENTITY002_','IDENTITY003_').replace('transactions_not_tested=1','transactions_tested=1 nested_not_tested=1')
payload='source='+repr(source)+'\n'+r'''
from pathlib import Path
import hashlib,json,shutil,subprocess
root=Path('/home/zoinve/harmony-virgl-883');work=root/'baremetal-identity-transactions-003'
local=Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/baremetal-identity-transactions-003')
assert not work.exists() and not local.exists();work.mkdir();local.mkdir()
(work/'init.c').write_text(source)
r=subprocess.run(['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-Werror',str(work/'init.c'),'-o',str(work/'init')],capture_output=True,text=True,timeout=60)
(local/'compile.stdout').write_text(r.stdout);(local/'compile.stderr').write_text(r.stderr)
assert r.returncode==0,r.stderr
binary=(work/'init').read_bytes()
emulator=shutil.which('qemu-aarch64');refusal_verified=False
if emulator:
 refusal=subprocess.run([emulator,str(work/'init')],capture_output=True,text=True,timeout=10)
 assert refusal.returncode==77,'non-PID1 guard failed'
 refusal_verified=True
report=dict(path=str(work/'init'),bytes=len(binary),sha256=hashlib.sha256(binary).hexdigest(),source_sha256=hashlib.sha256(source.encode()).hexdigest(),non_pid1_refusal_verified=refusal_verified,non_pid1_validation_limitation=None if emulator else 'qemu-aarch64 user-mode emulator unavailable',kernel_runtime_verified=False)
(work/'result.json').write_text(json.dumps(report,indent=2));(local/'result.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
'''
if __name__=='__main__':
    result=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=90)
    raise SystemExit(result.returncode)
