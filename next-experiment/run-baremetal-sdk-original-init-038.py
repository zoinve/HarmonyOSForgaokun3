"""Align current virt machine enumeration to the unchanged original fstab; retain RO originals."""
from pathlib import Path
import runpy
import subprocess

payload=runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-037.py')))['payload']
for old,new in [('baremetal-sdk-original-init-qemu-037','baremetal-sdk-original-init-qemu-038'),
                ('baremetal-sdk-original-init-037','baremetal-sdk-original-init-038'),
                ('harmony-sdk-qemu037-','harmony-sdk-qemu038-'),('ORIGINAL_INIT037_','ORIGINAL_INIT038_')]:
    assert old in payload;payload=payload.replace(old,new)
anchor='harmony.original_init_test=1 enforcing=1'
assert payload.count(anchor)==1
payload=payload.replace(anchor,anchor+' ohos.boot.hardware=hmos.emulator')
anchor='report=dict(bounded_observation_complete=False'
assert payload.count(anchor)==1
payload=payload.replace(anchor,'''# This exact guest enumerates virtio-mmio drives in reverse attachment order.
# The helper additionally rejects any mapping that does not match the original fstab.
command=command[:command.index('-drive')]
command+=['-drive','file='+str(scratch)+',if=none,id=sdkdata,format=raw',
 '-device','virtio-blk-device,drive=sdkdata,serial=sdk-testdata']
serials={'system.img':'sdk-system','vendor.img':'sdk-vendor','sys_prod.img':'sdk-sysprod'}
for i,(filename,row) in enumerate(reversed(list(images.items()))):
 identity='sdkro'+str(i)
 command+=['-drive','file='+row['path']+',if=none,id='+identity+',format=raw,readonly=on',
  '-device','virtio-blk-device,drive='+identity+',serial='+serials[filename]]
'''+anchor)
anchor="  report['helper_failure_observed']=b'ORIGINAL_INIT038_FAIL' in data"
assert payload.count(anchor)==1
payload=payload.replace(anchor,anchor+"\n  report['original_fstab_and_hardware_guard_observed']=b'ORIGINAL_INIT038_LAYOUT_GUARDED' in data")
compile(payload,'original-init-038-qemu','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=360)
    raise SystemExit(r.returncode)
