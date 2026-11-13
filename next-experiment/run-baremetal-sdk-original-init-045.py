"""Observe a real SA Check reply; full-system readiness always remains separate."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-044.py')))['payload']
for old,new in [('original-init-qemu-044','original-init-qemu-045'),('original-init-044','original-init-045'),
                ('harmony-sdk-qemu044-','harmony-sdk-qemu045-'),('ORIGINAL_INIT044_','ORIGINAL_INIT045_'),
                ('MANAGER_LIST_','MANAGER_CHECK_'),('genuine_manager_list_reply_under_enforcing_policy_observed',
                 'genuine_manager_check_reply_under_enforcing_policy_observed'),
                ('genuine_list_terminal_rejection_observed','genuine_check_terminal_rejection_observed')]:
 assert old in payload,old
 payload=payload.replace(old,new)
anchor="  report['sa_list_semantically_verified']=False"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"  report['genuine_remote_sa_object_observed']='ORIGINAL_INIT045_REMOTE_OBJECT sa_id=1912 ' in serial.read_text(errors='replace')\n"+anchor)
compile(payload,'original-init-045-run','exec')
if __name__=='__main__':
 r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=360)
 raise SystemExit(r.returncode)
