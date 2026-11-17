"""Compile the reference namespace launcher, not a replacement appspawn."""
import subprocess
payload=r'''
from pathlib import Path
import runpy,hashlib,json,subprocess,shutil
root=Path('/home/zoinve/harmony-virgl-883');base=Path('/mnt/d/lab/HarmonyOSForMatebookego')
work=root/'commercial-reference-namespace-036';local=base/'reports/commercial-reference-namespace-036'
assert not work.exists() and not local.exists()
p=runpy.run_path(str(base/'next-experiment/commercial-reference-namespace-036.py'))
work.mkdir();local.mkdir();src=work/'appspawn-reference-namespace.c';src.write_text(p['source']())
binary=work/'appspawn-reference-namespace'
command=['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-Werror',str(src),'-o',str(binary)]
with (work/'build.stdout').open('xb') as out,(work/'build.stderr').open('xb') as err:
 subprocess.run(command,stdout=out,stderr=err,check=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result=dict(**p['provenance'](),source_sha256=sha(src),binary_sha256=sha(binary),command=command,
 static_namespace_exec_only=True,original_appspawn_replaced=False,target_runtime_verified=False)
(work/'result.json').write_text(json.dumps(result,indent=2))
for name in ['appspawn-reference-namespace.c','build.stdout','build.stderr','result.json']:shutil.copyfile(work/name,local/name)
print(json.dumps(result,indent=2))
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)
