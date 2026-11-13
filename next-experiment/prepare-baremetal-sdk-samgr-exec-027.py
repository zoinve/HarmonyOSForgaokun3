"""Match original read-only system mount's exec-transition semantics; preserve policy."""
from pathlib import Path
import runpy
import subprocess

parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-samgr-exec-026.py')))
source=parent['source']
anchor='MS_REMOUNT | MS_RDONLY | MS_NODEV | MS_NOSUID, "noload"'
assert source.count(anchor)==1
source=source.replace(anchor,'MS_REMOUNT | MS_RDONLY | MS_NODEV, "noload"')
anchor='    int error_pipe[2];'
assert source.count(anchor)==1
source=source.replace(anchor,'''    struct stat original;
    require(!stat("/system/bin/samgr", &original) && S_ISREG(original.st_mode) &&
            !(original.st_mode & (S_ISUID | S_ISGID)), "original executable has no setid bits");
'''+anchor)
source=source.replace('SELINUX026_','SELINUX027_')
payload='source='+repr(source)+'\n'+parent['payload'][parent['payload'].index('\nfrom pathlib import Path')+1:]
payload=payload.replace('baremetal-sdk-samgr-exec-026','baremetal-sdk-samgr-exec-027')
anchor="policy=dump('vendor.img'"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"""fstab=dump('vendor.img','/etc/fstab.hmos.emulator','original-fstab')
system_rows=[line.split() for line in fstab.read_text().splitlines() if line.split() and line.split()[0]=='/dev/block/vda']
assert len(system_rows)==1 and system_rows[0][1]=='/usr'
assert 'ro' in system_rows[0][3].split(',') and 'nosuid' not in system_rows[0][3].split(',')
"""+anchor)
compile(payload,'samgr-exec027-preparation','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)
