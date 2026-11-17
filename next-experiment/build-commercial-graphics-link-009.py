"""Rebuild own hardware code against the ISO runtime; no target deployment."""
import subprocess,sys
payload=r'''
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
r=Path('/home/zoinve/harmony-virgl-883');base=Path('/mnt/d/lab/HarmonyOSForMatebookego/next-experiment')
work=r/'commercial-graphics-link-009';local=base.parent/'reports/commercial-graphics-link-009'
if work.exists():assert '--resume-compile' in sys.argv and not (work/'result.json').exists()
else:work.mkdir();local.mkdir();(work/'runtime').mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
audit=r/'commercial-graphics-009-audit'
for source,name in [('original-libc.so','libc.so'),('original-libc++.so','libc++.so')]:
 p=audit/source;assert p.stat().st_size>100000
 shutil.copyfile(p,work/'runtime'/name)
old=r/'native-render-041';m=json.loads((old/'result.json').read_text())
assert sha(old/'composer-trace.cpp')==m['sha256']['composer-trace.cpp']
shutil.copyfile(old/'composer-trace.cpp',work/'composer-trace.cpp')
shutil.copyfile(old/'native-cursor-composer-041.h',work/'native-cursor-composer-041.h')
args=m['commands'][0][1:]
args=[x.replace(str(old),str(work)) for x in args]
headers=r/'sdk/native'
cmd=['clang++-19','--target=aarch64-linux-ohos','--sysroot='+str(headers/'sysroot'),
 '-resource-dir='+str(headers/'llvm/lib/clang/15.0.4'),'-stdlib=libc++','-nostdlib++','-nostdinc++',
 '-isystem',str(r/'window-bridge/toolchain/platform-cxx-headers'),
 '-isystem',str(headers/'llvm/include/libcxx-ohos/include/c++/v1'),
 '-fuse-ld=lld','-rtlib=compiler-rt','-L'+str(work/'runtime'),'-L'+str(headers/'llvm/lib/aarch64-linux-ohos'),
 '-Wl,-z,max-page-size=65536','-Wl,--trace']+args+[str(work/'runtime/libc++.so'),str(work/'runtime/libc.so')]
attempt=0
while (work/('link.stdout'+('.'+str(attempt) if attempt else ''))).exists():attempt+=1
suffix='.'+str(attempt) if attempt else ''
with (work/('link.stdout'+suffix)).open('xb') as out,(work/('link.stderr'+suffix)).open('xb') as err:
 result=subprocess.run(cmd,stdout=out,stderr=err,timeout=120)
for name in ['link.stdout','link.stderr']:shutil.copyfile(work/(name+suffix),local/(name+suffix))
assert result.returncode==0,(result.returncode,(work/('link.stderr'+suffix)).read_text())
trace=(work/('link.stdout'+suffix)).read_text()
assert '/platform-root/' not in trace
assert not any('/sdk/' in line and line.strip().endswith('.so') for line in trace.splitlines())
elf=subprocess.check_output(['aarch64-linux-gnu-readelf','-d',str(work/'libdisplay_composer_vdi_impl.z.so')],text=True)
data=dict(sha256=sha(work/'libdisplay_composer_vdi_impl.z.so'),commands=[cmd],link_trace_file='link.stdout'+suffix,
 runtime_sha256={p.name:sha(p) for p in (work/'runtime').iterdir()},dynamic=elf,
 sdk_system_libraries_used=False,original_commercial_libc_and_libcxx=True,
 original_services_replaced=False,deployed=False,target_abi_verified=False,desktop_verified=False)
for p in [work/'result.json',local/'result.json']:p.open('x').write(json.dumps(data,indent=2))
assert sha(old/'composer-trace.cpp')==m['sha256']['composer-trace.cpp']
print(json.dumps(data,indent=2))
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-']+sys.argv[1:],input=payload,text=True,timeout=180).returncode)
