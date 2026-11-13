"""Use the SDK's real device-node policy in the isolated original-API test."""
from pathlib import Path
import runpy
import subprocess

base=Path(__file__).resolve().parent
parent=runpy.run_path(str(base/'prepare-baremetal-identity-sdk-006.py'))
source=parent['source'];anchor='    pid_t sdk_child=fork();'
assert source.count(anchor)==1
source=source.replace(anchor,'''    require(chown("/dev/access_token_id",3020,3020)==0&&chmod("/dev/access_token_id",0666)==0,"original SDK ueventd device policy inside QEMU only");
    pid_t sdk_child=fork();''')
source=source.replace('IDENTITY006_','IDENTITY007_')
sdk_source=parent['sdk_source'].replace('SDK006_','SDK007_')
assert sdk_source.count('gid_t group=77;')==1
sdk_source=sdk_source.replace('gid_t group=77;','gid_t group=3020;')
payload=parent['payload'];start=payload.index('from pathlib import Path')
payload='source='+repr(source)+'\nsdk_source='+repr(sdk_source)+'\n'+payload[start:]
payload=payload.replace('baremetal-identity-sdk-006','baremetal-identity-sdk-007')
anchor="system='/mnt/d/Download/pc_all_arm/system.img'"
assert payload.count(anchor)==1
payload=payload.replace(anchor,anchor+'''
ueventd=run(['debugfs','-R','cat /system/etc/ueventd.config',system],'original-ueventd')
assert '/dev/access_token_id 0666 3020 3020' in ueventd.splitlines()
''')
payload=payload.replace('images_modified=False)','images_modified=False,original_device_policy_verified=True,ueventd_sha256=hashlib.sha256(ueventd.encode()).hexdigest())')
compile(payload,'prepare-sdk-007','exec')
if __name__=='__main__':
    result=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(result.returncode)
