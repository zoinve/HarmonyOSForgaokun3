"""Independent accelerated rotation composer; retain the original 032 bridge."""
import subprocess
payload=r'''
from pathlib import Path
import subprocess,hashlib,json,shutil
root=Path('/home/zoinve/harmony-virgl-883');base=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
old=root/'native-cursor-032-r2';work=root/'native-render-034'
local=base.parent/'reports/native-render-034'
assert not work.exists() and not local.exists()
work.mkdir();local.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((old/'result.json').read_text())
for n,h in r['sha256'].items():assert sha(old/n)==h
s=(old/'composer-trace.cpp').read_text()
assert s.count('#include "native-cached-copy-024.h"')==1
assert s.count('cached_landscape_copy_024(')==1
s=s.replace('#include "native-cached-copy-024.h"','#include "native-cached-copy-034.h"',1).replace('cached_landscape_copy_024(','cached_landscape_copy_034(',1)
(work/'composer-trace.cpp').write_text(s)
for n in ['libcursor_drawing_adapter.z.so','libcursor_drawing_adapter032.z.so']:shutil.copyfile(old/n,work/n)
cmd=[a.replace(str(old),str(work)) for a in r['commands'][1]]
q=subprocess.run(cmd,text=True,capture_output=True)
(local/'compile.stdout').write_text(q.stdout);(local/'compile.stderr').write_text(q.stderr)
assert q.returncode==0,q.stderr
for n,h in r['sha256'].items():assert sha(old/n)==h
names=list(r['sha256'])
result=dict(sha256={n:sha(work/n) for n in names},commands=[cmd],
 original_cursor_032_unchanged=True,input_injection=False,installed=False,runtime_verified=False,
 acceleration='AArch64 NEON exact-size rotation plus removal of intermediate frame copy; NOT GPU rotation',
 scaling_fallback_retained=True,desktop_120fps_verified=False)
for p in [work/'result.json',local/'result.json']:
 with p.open('x') as f:json.dump(result,f,indent=2)
for n in names:shutil.copyfile(work/n,local/n)
print(json.dumps(result,indent=2))
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180).returncode)
