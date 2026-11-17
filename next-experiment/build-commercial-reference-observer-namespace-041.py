"""Retain L410's exact namespace main; add only the transparent original-method observer."""
from pathlib import Path
import runpy,subprocess,json,hashlib,shutil
base=Path(__file__).resolve().parents[1];root=Path('/home/zoinve/harmony-virgl-883')
work=root/'commercial-rs-observer-041'
original=runpy.run_path(str(base/'next-experiment/commercial-reference-namespace-036.py'))['source']()
old='static const char *kPreload = "libappspawn_helper.z.so";'
assert original.count(old)==1
source=original.replace(old,'static const char *kPreload = "libappspawn_helper.z.so:/system/lib64/libcommercial_rs_observer041.so";',1)
assert source[source.index('int main('):]==original[original.index('int main('):]
p=work/'namespace-observer041.c';assert not p.exists();p.write_text(source)
binary=work/'appspawn-reference-namespace'
subprocess.run(['aarch64-linux-gnu-gcc','-static','-O2','-Wall','-Wextra','-Werror',str(p),'-o',str(binary)],check=True,timeout=30)
result=dict(source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),reference_main_unchanged=True,original_appspawn_helper_retained=True,identity_sandbox_argv_unchanged=True)
with (work/'namespace-result.json').open('x') as out:json.dump(result,out,indent=2)
for name in [p.name,'namespace-result.json']:shutil.copyfile(work/name,base/'reports/commercial-rs-observer-041'/name)
print(json.dumps(result))
