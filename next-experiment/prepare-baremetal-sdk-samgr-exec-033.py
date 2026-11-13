"""Policy-authorized direct-child register observations; no substitute service or policy edits."""
from pathlib import Path
import runpy
import subprocess

parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-samgr-exec-032.py')))
source=parent['source']
anchor='static void samgr_waitpoints_031(pid_t child)'
assert source.count(anchor)==1
source=source.replace(anchor,Path(__file__).with_name('baremetal-sdk-samgr-trace-033.h').read_text()+'\n'+anchor)
anchor='    if (!exited) samgr_waitpoints_031(child);'
assert source.count(anchor)==1
source=source.replace(anchor,anchor+'\n    if (!exited) samgr_trace_033(child);')
source=source.replace('SELINUX032_','SELINUX033_')
payload='source='+repr(source)+'\n'+parent['payload'][parent['payload'].index('\nfrom pathlib import Path')+1:]
payload=payload.replace('baremetal-sdk-samgr-exec-032','baremetal-sdk-samgr-exec-033')
compile(payload,'samgr-exec033-preparation','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)
