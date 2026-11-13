"""Prepare original-policy identity checks plus read-only SDK filesystem inspection."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
parent=runpy.run_path(str(base/'prepare-baremetal-selinux-identity-023.py'))
source=parent['source']
anchor='int main(void)'
assert source.count(anchor)==1
source=source.replace(anchor,(base/'baremetal-sdk-system-read-025.h').read_text()+'\n'+anchor)
anchor='    original_device_020("access_token_id");'
assert source.count(anchor)==1
source=source.replace(anchor,'    mount_original_system_025();\n'+anchor)
anchor='    identity_under_policy_020();'
assert source.count(anchor)==1
source=source.replace(anchor,anchor+'\n    inspect_original_system_025();').replace('SELINUX023_','SELINUX025_')
payload='source='+repr(source)+'\n'+parent['payload'][parent['payload'].index('\nfrom pathlib import Path')+1:]
payload=payload.replace('baremetal-selinux-identity-023','baremetal-sdk-system-read-025')
compile(payload,'sdk-system-read-025-preparation','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)
