"""Provide genuine kernel urandom using original SDK device policy; no fabricated entropy."""
from pathlib import Path
import runpy
import subprocess

parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-samgr-exec-028.py')))
source=parent['source']
anchor='    mount_original_system_025();'
assert source.count(anchor)==1
source=source.replace(anchor,anchor+'''
    require(!mknod("/dev/urandom", S_IFCHR | 0666, makedev(1,9)) && !chmod("/dev/urandom", 0666),
            "genuine kernel urandom with original SDK mode");''')
anchor='    samgr_exec_026();'
assert source.count(anchor)==1
source=source.replace(anchor,'''    const char random_context[] = "u:object_r:dev_random_file:s0";
    require(!setxattr("/dev/urandom", "security.selinux", random_context, sizeof(random_context), 0),
            "original SDK urandom security label");
'''+anchor)
source=source.replace('SELINUX028_','SELINUX029_')
payload='source='+repr(source)+'\n'+parent['payload'][parent['payload'].index('\nfrom pathlib import Path')+1:]
payload=payload.replace('baremetal-sdk-samgr-exec-028','baremetal-sdk-samgr-exec-029')
anchor="policy=dump('vendor.img'"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"""contexts=dump('system.img','/system/etc/selinux/targeted/contexts/file_contexts','original-device-contexts')
assert any(line.split()==['/dev/urandom','u:object_r:dev_random_file:s0'] for line in contexts.read_text().splitlines())
ueventd=dump('system.img','/system/etc/ueventd.config','original-ueventd.config')
assert any(line.split()==['/dev/urandom','0666','0','0'] for line in ueventd.read_text().splitlines())
"""+anchor)
compile(payload,'samgr-exec029-preparation','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)
