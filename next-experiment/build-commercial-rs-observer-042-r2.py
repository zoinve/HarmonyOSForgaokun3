"""Compile exported-method observation against the real commercial C++ runtime."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess
base=Path(__file__).resolve().parents[1];root=Path('/home/zoinve/harmony-virgl-883')
work=root/'commercial-rs-observer-042-r2';local=base/'reports/commercial-rs-observer-042-r2'
assert not work.exists() and not local.exists();work.mkdir();local.mkdir()
source=base/'next-experiment/commercial-rs-observer-042.cpp';shutil.copyfile(source,work/source.name)
manifest=json.loads((base/'reports/commercial-graphics-014/result.json').read_text())
command=manifest['commands'][0][:manifest['commands'][0].index('-shared')]
runtime=root/'commercial-graphics-014/runtime';new=work/'libcommercial_rs_observer042.so'
command+=['-shared','-fPIC','-O2','-std=c++17','-Wall','-Wextra','-Werror',str(work/source.name),str(runtime/'libc++.so'),str(runtime/'libc.so'),'-ldl','-pthread','-Wl,--no-undefined','-Wl,-soname,libcommercial_rs_observer042.so','-o',str(new)]
with (work/'build.stdout').open('xb') as out,(work/'build.stderr').open('xb') as err:subprocess.run(command,stdout=out,stderr=err,check=True,timeout=120)
references={}
for p in Path('/tmp/commercial-rs-boundary-039').glob('*.so'):
 if p.stat().st_size<4:continue
 for l in subprocess.check_output(['aarch64-linux-gnu-nm','-D','--defined-only',str(p)],text=True).splitlines():
  if l.split():references[l.split()[-1]]=p.name
symbols=[]
for l in subprocess.check_output(['aarch64-linux-gnu-nm','-D','--defined-only',str(new)],text=True).splitlines():
 n=l.split()[-1]
 if n.startswith('_ZN4OHOS5Rosen'):
  assert n in references,n
  symbols.append(dict(symbol=n,original_library=references[n]))
assert len(symbols)==11,symbols
# Resolve-by-name strings must match the exact exported methods, including __h ABI.
strings=re.findall(r'original042<Fn>\("([^"]+)"\)',source.read_text())+re.findall(r'FLUSH042\([^,]+,"([^"]+)"',source.read_text())
assert set(strings)=={r['symbol'] for r in symbols}
trace=(work/'build.stdout').read_text()
assert not any('/sdk/' in l and l.strip().endswith('.so') for l in trace.splitlines())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
result=dict(command=command,source_sha256=sha(source),library_sha256=sha(new),library_bytes=new.stat().st_size,observed_original_symbols=symbols,sdk_runtime_libraries_used=False,private_object_layouts_read=False,original_calls_forwarded=True,max_log_records_per_process=594,target_verified=False,desktop_verified=False)
(work/'result.json').write_text(json.dumps(result,indent=2))
for name in [source.name,'build.stdout','build.stderr','result.json']:shutil.copyfile(work/name,local/name)
print(json.dumps(result,indent=2))
