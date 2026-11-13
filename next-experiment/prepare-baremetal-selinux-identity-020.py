"""Exercise real token/Binder permission boundaries with original enforcing production policy."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
parent=runpy.run_path(str(base/'prepare-baremetal-selinux-load-019.py'))
source=parent['source']
anchor='int main(void)'
assert source.count(anchor)==1
source=source.replace(anchor,(base/'baremetal-selinux-identity-020.h').read_text()+'\n'+anchor)
anchor='    const char console_context[] = "u:object_r:dev_console_file:s0";'
assert source.count(anchor)==1
source=source.replace(anchor,'    original_device_020("access_token_id");\n    original_device_020("binder");\n'+anchor)
anchor='    /* Loading the unchanged production policy is not a service/domain-transition test. */'
assert source.count(anchor)==1
source=source.replace(anchor,'    identity_under_policy_020();\n    /* This is not a full service boot or SDK transaction test. */')
source=source.replace('SELINUX019_','SELINUX020_')
payload='source='+repr(source)+'\n'+parent['payload'][parent['payload'].index('\nfrom pathlib import Path')+1:]
payload=payload.replace('baremetal-selinux-load-019','baremetal-selinux-identity-020')
compile(payload,'selinux-identity-020-preparation','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)
