"""Explicit directories before immutable 016 hardware, final 017 init afterward."""
from pathlib import Path
import subprocess
payload=r'''
from pathlib import Path
import ast,stat,gzip,hashlib,json
root=Path('/home/zoinve/harmony-virgl-883');base=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
work=root/'commercial61-native-017';local=base.parent/'reports/commercial61-native-017'
t=ast.parse((base/'build-native-return-overlay-033.py').read_text())
s=next(x.value.value for x in t.body if isinstance(x,ast.Assign) and any(isinstance(k,ast.Name) and k.id=='payload' for k in x.targets))
a=ast.parse(s);ns={}
exec(compile(ast.Module(body=[x for x in a.body if isinstance(x,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),'<archive-helpers>','exec'),ns)
parse=ns['parse'];member=ns['member']
old=parse(root/'commercial61-native-001/initrd.img')
broken=parse(root/'commercial61-native-016-r2/minimal-overlay.img')
new=parse(work/'initrd.img')
added={n for n in new if n not in old and stat.S_ISDIR(new[n][0])}
assert len(added)==13 and all(n.startswith('native-target/graphics016') for n in added)
patch={n:new[n] for n in added|{'init'}}
assert new['native-target/bootstrap']==broken['native-target/bootstrap']
state=dict(old)
for archive in [patch,broken,patch]:
 for name in sorted(archive):
  if name.startswith('native-target/graphics016/'):
   for parent in Path(name).parents:
    if str(parent)=='.':continue
    assert str(parent) in state and stat.S_ISDIR(state[str(parent)][0]),('missing parent at extraction',name,str(parent))
  state[name]=archive[name]
assert state==new, 'ordered four-initrd chain differs from full 017'
data=b''.join(member(n,m,d,i+1) for i,(n,(m,d)) in enumerate(sorted(patch.items())))
data+=member('TRAILER!!!',0,b'',len(patch)+1)
blob=gzip.compress(data,compresslevel=9,mtime=0)
with (work/'minimal-overlay.img').open('xb') as f:f.write(blob)
assert parse(work/'minimal-overlay.img')==patch
result=dict(bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest(),members=sorted(patch),
 chain=['commercial61-native-001/initrd.img','commercial61-native-017/initrd.img','commercial61-native-016/initrd.img','commercial61-native-017/initrd.img'],
 existing_016_overlay_sha256=hashlib.sha256((root/'commercial61-native-016-r2/minimal-overlay.img').read_bytes()).hexdigest(),
 parent_directories_present_before_hardware_files=True,ordered_chain_equals_full_017=True,
 original_images_written=False,sdk_payload=False,runtime_verified=False)
for p in [work/'overlay-result.json',local/'overlay-result.json']:
 with p.open('x') as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)
