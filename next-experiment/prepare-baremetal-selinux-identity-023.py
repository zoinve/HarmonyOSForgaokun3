"""Distinguish SELinux-blocked version query from honestly unsupported allowed SPM request."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
parent=runpy.run_path(str(base/'prepare-baremetal-selinux-identity-022.py'))
source=parent['source']
old='''    require(ioctl(token, _IOR('A', 25, uint32_t), &version) == -1 && errno == EOPNOTSUPP &&
            version == 0xa5a5a5a5U, "unsupported SPM remains honestly unsupported under policy");'''
new='''    require(ioctl(token, _IOR('A', 25, uint32_t), &version) == -1 && errno == EACCES &&
            version == 0xa5a5a5a5U, "original policy denies init SPM version query");
    uint64_t spm_request = 0;
    errno = 0;
    require(ioctl(token, _IOWR('A', 16, uint64_t), &spm_request) == -1 && errno == EOPNOTSUPP &&
            spm_request == 0, "policy allowed SPM command remains honestly unsupported by driver");'''
assert source.count(old)==1
source=source.replace(old,new).replace('SELINUX022_','SELINUX023_').replace('spm_unsupported=1','spm_version_policy_denied=1 spm_allowed_command_unsupported=1')
payload='source='+repr(source)+'\n'+parent['payload'][parent['payload'].index('\nfrom pathlib import Path')+1:]
payload=payload.replace('baremetal-selinux-identity-022','baremetal-selinux-identity-023')
compile(payload,'selinux-identity-023-preparation','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)
