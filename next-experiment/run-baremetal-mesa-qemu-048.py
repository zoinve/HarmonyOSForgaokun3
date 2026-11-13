"""Diskless ARM64 check: missing render device fails closed and leaves no private mounts."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
harness=(base/'baremetal-native-identity-qemu-047.c').read_text().replace('NATIVE_READ047_','NATIVE_MESA048_')
harness=harness.replace('    pid_t child=fork();CHECK(child>=0);','    int logs[2];CHECK(!pipe(logs));\n    pid_t child=fork();CHECK(child>=0);')
harness=harness.replace('if(!child){execl("/probe","/probe",NULL);_exit(126);}',
    'if(!child){close(logs[0]);CHECK(dup2(logs[1],1)==1 && dup2(logs[1],2)==2);close(logs[1]);execl("/probe","/probe",NULL);_exit(127);}')
harness=harness.replace('    int status=0;CHECK(waitpid(child,&status,0)==child);',
    '    close(logs[1]);char output[4096];ssize_t n;while((n=read(logs[0],output,sizeof(output)))>0)CHECK(write(1,output,n)==n);close(logs[0]);\n    int status=0;CHECK(waitpid(child,&status,0)==child);')
harness=harness.replace('(refusal?77:0)','(refusal?77:126)').replace('/run/identity-read-002','/run/native-mesa-root-001')
parent=runpy.run_path(str(base/'run-baremetal-native-identity-qemu-047.py'))['payload']
payload='sources='+repr({'baremetal-mesa-qemu-048.c':harness,'baremetal-mesa-launcher-001.c':(base/'baremetal-mesa-launcher-001.c').read_text()})+'\n'+parent[parent.index('\nfrom pathlib import Path')+1:]
for old,new in [('baremetal-native-identity-qemu-047','baremetal-mesa-qemu-048'),('baremetal-native-identity-read-002.c','baremetal-mesa-launcher-001.c'),('NATIVE_READ047_','NATIVE_MESA048_')]:
    assert old in payload,old
    payload=payload.replace(old,new)
old="assert 'requires diagnostic kernel and opt-in' in log and 'child_status=77 mountpoint_removed=1' in log and 'NATIVE_IDENTITY_READ002_PASS' not in log"
assert payload.count(old)==1
payload=payload.replace(old,"assert 'requires diagnostic kernel and enforcing opt-in' in log and 'child_status=77 mountpoint_removed=1' in log and 'NATIVE_MESA001_SANDBOX' not in log")
old="assert 'NATIVE_IDENTITY_READ002_PASS protocol=8 features=5 legacy_binder=1 selinux_active=1 enforcing=1' in log\n   assert 'policy_loaded_by_probe=0 transactions_not_tested=1' in log and 'child_status=0 mountpoint_removed=1' in log"
assert payload.count(old)==1
payload=payload.replace(old,"assert 'NATIVE_MESA001_FAIL operation=exact render node identity' in log\n   assert 'NATIVE_MESA001_END status=126' in log and 'child_status=126 mountpoint_removed=1' in log and 'NATIVE_MESA001_SANDBOX' not in log")
compile(payload,'mesa048-diskless-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)
