"""Own diagnostic C executable; imports only the target's original libc and config library."""
import subprocess
payload=r'''
from pathlib import Path
import subprocess,json,hashlib
root=Path('/home/zoinve/harmony-virgl-883');base=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
work=root/'commercial-profile-005';assert not work.exists();work.mkdir()
cmd=['clang-19','--target=aarch64-linux-ohos','--sysroot='+str(root/'sdk/native/sysroot'),'-resource-dir='+str(root/'sdk/native/llvm/lib/clang/15.0.4'),'-fuse-ld=lld','-rtlib=compiler-rt','-L'+str(root/'sdk/native/llvm/lib/aarch64-linux-ohos'),'-O2','-Wall','-Wextra','-Werror',str(base/'commercial-profile-005.c'),'-ldl','-o',str(work/'samgr-observe')]
r=subprocess.run(cmd,capture_output=True);(work/'compile.stdout').write_bytes(r.stdout);(work/'compile.stderr').write_bytes(r.stderr);assert r.returncode==0,r.stderr.decode()
result=dict(sha256=hashlib.sha256((work/'samgr-observe').read_bytes()).hexdigest(),command=cmd,identity_changed=False,runtime_verified=False)
(work/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True).returncode)
