"""Prepare a bounded original-samgr exec/domain observation, not a complete service boot."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
parent=runpy.run_path(str(base/'prepare-baremetal-sdk-system-read-025.py'))
source=parent['source']
anchor='int main(void)'
assert source.count(anchor)==1
source=source.replace(anchor,(base/'baremetal-sdk-samgr-exec-026.h').read_text()+'\n'+anchor)
anchor='    mount_original_system_025();'
assert source.count(anchor)==1
source=source.replace(anchor,anchor+'\n    require(!symlink("/sdk-system/system", "/system") && !symlink("/system/lib", "/lib"), "original SDK executable and interpreter paths");')
anchor='    inspect_original_system_025();'
assert source.count(anchor)==1
source=source.replace(anchor,anchor+'\n    samgr_exec_026();').replace('SELINUX025_','SELINUX026_')
payload='source='+repr(source)+'\n'+parent['payload'][parent['payload'].index('\nfrom pathlib import Path')+1:]
payload=payload.replace('baremetal-sdk-system-read-025','baremetal-sdk-samgr-exec-026')
compile(payload,'sdk-samgr-exec-026-preparation','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)
