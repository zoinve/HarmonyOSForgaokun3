"""Cross-build and package an isolated OHOS render test; never deploy or execute it."""
from pathlib import Path
import runpy
import subprocess

base = Path(__file__).resolve().parent
out = base.parent / 'reports/baremetal-freedreno-probe-package-001'
source = runpy.run_path(str(base / 'baremetal-freedreno-probe-001.py'))['build_source']()
header = (base / 'baremetal-freedreno-policy-001.h').read_text()
payload = 'source=' + repr(source) + '\nheader=' + repr(header) + '\n' + r'''
from pathlib import Path
import hashlib,json,re,shutil,subprocess,tarfile
root=Path('/home/zoinve/harmony-virgl-883');work=root/'baremetal-freedreno-probe-001'
assert not work.exists();work.mkdir()
bundle=work/'bundle';bundle.mkdir();libs=bundle/'lib';libs.mkdir()
report=Path('/mnt/d/lab/HarmonyOSForMatebookego/reports/baremetal-freedreno-probe-package-001')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
stage=root/'baremetal-mesa-freedreno-002/stage/system/lib64/lab-freedreno002'
built=json.loads((root/'baremetal-mesa-freedreno-002/result.json').read_text());assert built['build_success']
inputs=[]
def copy(src,name,expected=None):
    digest=sha(src)
    if expected:assert digest==expected,str(src)
    dst=libs/name;shutil.copyfile(src,dst);dst.chmod(0o555)
    inputs.append(dict(source=str(src),destination='lib/'+name,sha256=digest,bytes=src.stat().st_size))
copy(Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment/official-gpu-probe-924/official-loader.so'),
     'ld-musl-aarch64.so.1','f7947b746dc4169677321b18ee77e4f4f158fde75762b2d9a3ae107b277c0181')
(libs/'libc.so').symlink_to('ld-musl-aarch64.so.1')
copy(root/'sdk/native/llvm/lib/aarch64-linux-ohos/libc++_shared.so','libc++_shared.so',
     'b0455e6756bc102afa17b6bbfc934d941bbfb7db4d7d5e74ef453fb770274230')
copy(root/'prefix/system/lib64/lab-virgl883/libdrm.so.2.124.0','libdrm.so.2',
     '5c487a67afaa4ad6dbfabe1fa0dc7949598d1977859bbb464d9f6a9c3b6e9aa3')
for src,name,digest in [
 ('libEGL.so.1.0.0','libEGL.so.1','2609f78303699bb7bf1ec47ddf2e7562322e8a70b21da92e86d82456e5855694'),
 ('libGLESv2.so.2.0.0','libGLESv2.so.2','6f3f4ea3930c3a67e971d302df54393da76602f03dae2c35c7b35b886940b162'),
 ('libgbm.so.1.0.0','libgbm.so.1','eaf90b35488944e0a15e85f1c79684c7bcbb78e00aadead413046affc432ffff'),
 ('libgallium-25.0.1.so','libgallium-25.0.1.so','755f1e9048db6b7f442d1b2cb0b13ee5527635a2f3f8623ce198bfac93d6985e')]:
 copy(stage/src,name,digest)
(work/'probe.c').write_text(source);(work/'baremetal-freedreno-policy-001.h').write_text(header)
args=[str(root/'toolchain/ohos-cc'),'-O2','-Wall','-Wextra','-Werror','-fno-emulated-tls',
 '-I'+str(root/'prefix/system/include'),'-I'+str(work),str(work/'probe.c'),
 '-L'+str(stage),'-L'+str(root/'prefix/system/lib64/lab-virgl883'),'-lEGL','-lGLESv2',
 '-Wl,-rpath,$ORIGIN/lib','-o',str(bundle/'probe')]
r=subprocess.run(args,capture_output=True,text=True,timeout=60)
(report/'compile.stdout').write_text(r.stdout);(report/'compile.stderr').write_text(r.stderr);r.check_returncode()
rows=[];closure={};defined=set();undefined=set()
for p in sorted(bundle.rglob('*')):
 if not p.is_file() or p.is_symlink():continue
 h=subprocess.check_output(['readelf','-h',str(p)],text=True);assert 'AArch64' in h
 d=subprocess.check_output(['readelf','-d',str(p)],text=True)
 needs=re.findall(r'\(NEEDED\).*\[(.*?)\]',d)
 for n in needs:assert (libs/n).is_file(),(str(p),n)
 closure[str(p.relative_to(bundle))]=needs
 syms=subprocess.check_output(['readelf','--dyn-syms','--wide',str(p)],text=True)
 for line in syms.splitlines():
  fields=line.split()
  if len(fields)<8 or fields[4] not in ('GLOBAL','WEAK'):continue
  name=fields[7].split('@')[0]
  if fields[6]=='UND':
   if fields[4]=='GLOBAL':undefined.add(name)
  else:defined.add(name)
 rows.append(dict(path=str(p.relative_to(bundle)),bytes=p.stat().st_size,sha256=sha(p)))
assert not undefined-defined,sorted(undefined-defined)
manifest=dict(files=rows,symlinks={'lib/libc.so':'ld-musl-aarch64.so.1'},inputs=inputs,
 dependency_closure=closure,all_strong_dynamic_symbols_resolved=True,
 source_sha256=sha(work/'probe.c'),policy_sha256=sha(work/'baremetal-freedreno-policy-001.h'),
 build_command=args,gpu_execution_verified=False,desktop_verified=False)
(bundle/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
archive=report/'bundle.tar.gz'
with tarfile.open(archive,'w:gz',dereference=False) as tar:
 for p in sorted(bundle.rglob('*')):tar.add(p,arcname=str(p.relative_to(bundle)),recursive=False)
manifest['archive_sha256']=sha(archive);manifest['archive_bytes']=archive.stat().st_size
(report/'package.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(dict(files=len(rows),strong_symbols_resolved=True,archive_bytes=archive.stat().st_size,
 archive_sha256=sha(archive),gpu_execution_verified=False)))
'''

if __name__ == '__main__':
    assert not out.exists()
    compile(payload, 'freedreno-package-001', 'exec')
    out.mkdir()
    subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,check=True,timeout=120)
