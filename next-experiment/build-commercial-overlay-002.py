"""Prove the commercial base changes only its two Linux bootstrap executables."""
from pathlib import Path
import runpy,subprocess
payload=r'''
from pathlib import Path
import ast,gzip,hashlib,json,runpy
base=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment');root=Path('/home/zoinve/harmony-virgl-883')
tree=ast.parse(runpy.run_path(str(base/'build-native-return-overlay-033.py'))['payload'])
ns={};exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),'<archive-helpers>','exec'),ns)
parse=ns['parse'];member=ns['member'];work=root/'commercial61-native-002';local=base.parent/'reports/commercial61-native-002'
old=parse(root/'commercial61-native-001/initrd.img');new=parse(work/'initrd.img')
assert old.keys()==new.keys()
changed={n for n in old if old[n]!=new[n]}
assert changed=={'init','native-target/bootstrap'},changed
data=b''.join(member(n,new[n][0],new[n][1],i+1) for i,n in enumerate(sorted(changed)))+member('TRAILER!!!',0,b'',3)
dest=work/'minimal-overlay.img'
dest.open('xb').write(gzip.compress(data,mtime=0))
assert old|parse(dest)==new
r=dict(sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),bytes=dest.stat().st_size,changed_members=sorted(changed),base_commercial_candidate=1,commercial_libraries_unchanged=True,sdk_payload=False)
for p in [work/'overlay-result.json',local/'overlay-result.json']:p.open('x').write(json.dumps(r,indent=2))
print(json.dumps(r,indent=2))
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)
