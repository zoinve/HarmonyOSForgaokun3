"""Keep 030 userspace unchanged; boot the independently rebuilt namespace-safe kernel."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-native-original-graphics-boot-030.py'))
inner=p['inner']
outer=p['outer'].replace('native-interactive-030-%s','native-interactive-031-%s').replace('NATIVE_INTERACTIVE030','NATIVE_INTERACTIVE031')
# Capture file names remain 030 to preserve byte-identical userspace behavior.
payload=p['payload'].replace('native-original-graphics-boot-030','native-original-graphics-boot-031')
payload=payload.replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
anchor='artifacts=[]'
assert payload.count(anchor)==1
addition=r'''
kernel_work=root/'native-binder-kernel-031'
kernel_result=json.loads((kernel_work/'result.json').read_text())
kernel_source=Path(kernel_result['image'])
assert kernel_result['old_source_config_unchanged'] and kernel_result['real_pid_reference_lifetime']
assert kernel_result['release']=='7.1.0-rc3-gaokun3-el2'
assert sha(kernel_source)==kernel_result['sha256']
shutil.copyfile(kernel_source,work/'linux')
assert sha(work/'linux')==kernel_result['sha256']
with (local/'binder-pid-repair-031.json').open('x') as f:
 json.dump(dict(kernel=kernel_result,userspace_unchanged_from_030=True,
   receiver_namespace_pid=True,sender_tokens_unchanged=True,namespace_isolation_retained=True,
   application_checks_unchanged=True,runtime_fix_verified=False),f,indent=2)
'''
payload=payload.replace(anchor,addition+'\n'+anchor,1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
