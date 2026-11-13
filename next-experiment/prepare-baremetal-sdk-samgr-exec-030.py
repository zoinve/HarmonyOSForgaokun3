"""Require a real Binder response from the original samgr under production enforcing policy."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
parent=runpy.run_path(str(base/'prepare-baremetal-sdk-samgr-exec-029.py'))
source=parent['source']
anchor='static void samgr_exec_026(void)'
assert source.count(anchor)==1
source=source.replace(anchor,(base/'baremetal-sdk-samgr-ping-030.h').read_text()+'\n'+anchor)
anchor='    close(error_pipe[0]);\n    if (!exited) {'
assert source.count(anchor)==1
source=source.replace(anchor,'    int ping_ok = !exited && samgr_ping_030();\n'+anchor)
anchor='    require(!exec_error && exec_pipe_closed && observed, "original samgr actual exec domain and unprivileged credentials");'
assert source.count(anchor)==1
source=source.replace(anchor,anchor+'\n    require(ping_ok, "original samgr context manager returns real Binder ping");')
source=source.replace('SELINUX029_','SELINUX030_')
payload='source='+repr(source)+'\n'+parent['payload'][parent['payload'].index('\nfrom pathlib import Path')+1:]
payload=payload.replace('baremetal-sdk-samgr-exec-029','baremetal-sdk-samgr-exec-030')
compile(payload,'samgr-exec030-preparation','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)
