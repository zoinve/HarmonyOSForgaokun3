"""Disposable native overlay DAC regression; no target services or GPU access."""
from pathlib import Path
import subprocess,json
PAYLOAD=r'''
from pathlib import Path
import os,subprocess,tempfile,json,stat,shutil
assert os.geteuid()==0
subprocess.run(['mount','--make-rprivate','/'],check=True)
results=[]
for mask in [0o077,0o022]:
 parent=Path(tempfile.mkdtemp(prefix='native-overlay-mask-004-',dir='/var/tmp'))
 os.chmod(parent,0o755);old=os.umask(0o022)
 lower=parent/'lower';lower.mkdir(mode=0o755)
 tool=lower/'tool';tool.write_text('not executed\n');tool.chmod(0o755)
 merged=parent/'merged';merged.mkdir(mode=0o755)
 os.umask(mask)
 upper=parent/'upper';upper.mkdir(mode=0o755)
 work=parent/'work';work.mkdir(mode=0o755)
 os.umask(old)
 try:
  subprocess.run(['mount','-t','overlay','overlay','-o',f'lowerdir={lower},upperdir={upper},workdir={work}',str(merged)],check=True)
  mode=stat.S_IMODE(merged.stat().st_mode)
  pid=os.fork()
  if pid==0:
   os.setgroups([]);os.setgid(65534);os.setuid(65534)
   os._exit(0 if os.access(merged/'tool',os.X_OK) else 1)
  _,status=os.waitpid(pid,0)
  results.append(dict(umask=oct(mask),merged_root_mode=oct(mode),unprivileged_access_exit=os.waitstatus_to_exitcode(status)))
 finally:
  subprocess.run(['umount',str(merged)],check=True)
  shutil.rmtree(parent)
assert results[0]['merged_root_mode']=='0o700' and results[0]['unprivileged_access_exit']==1
assert results[1]['merged_root_mode']=='0o755' and results[1]['unprivileged_access_exit']==0
print(json.dumps(dict(cases=results,target_services_executed=False,original_images_accessed=False),indent=2))
'''
if __name__=='__main__':
    r=subprocess.run(['ssh','matebook','sudo -n unshare --mount --fork python3 -'],input=PAYLOAD,text=True,capture_output=True,timeout=90)
    print(r.stdout);print(r.stderr,end='');r.check_returncode()
    out=Path(__file__).resolve().parent.parent/'reports/native-overlay-umask-regression-004.json'
    with out.open('x') as f:json.dump(json.loads(r.stdout),f,indent=2)
