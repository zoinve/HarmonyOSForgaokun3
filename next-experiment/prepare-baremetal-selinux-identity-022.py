"""Respect production getattr denials while exercising its separately allowed device operations."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
parent=runpy.run_path(str(base/'prepare-baremetal-selinux-identity-020.py'))
source=parent['source']
for path,label in [('access_token_id','token'),('binder','Binder')]:
    old=f'''    require(getxattr("/dev/{path}", "security.selinux", actual, sizeof(actual)-1) > 0 &&
            !strcmp(actual, {label.lower()}_label), "actual original {label}-device label");'''
    new=f'''    errno = 0;
    require(getxattr("/dev/{path}", "security.selinux", actual, sizeof(actual)-1) == -1 && errno == EACCES,
            "original production policy denies init {label} metadata read");'''
    assert source.count(old)==1,old
    source=source.replace(old,new)
source=source.replace('original_labels=1','original_labels_set=1 metadata_read_denied=1').replace('SELINUX020_','SELINUX022_')
payload='source='+repr(source)+'\n'+parent['payload'][parent['payload'].index('\nfrom pathlib import Path')+1:]
payload=payload.replace('baremetal-selinux-identity-020','baremetal-selinux-identity-022')
compile(payload,'selinux-identity-022-preparation','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)
