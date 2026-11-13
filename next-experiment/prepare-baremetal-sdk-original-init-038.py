"""Require the original emulator hardware/fstab disk contract before genuine init handoff."""
from pathlib import Path
import runpy
import subprocess

parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-037.py')))
source=parent['source']
anchor='    if (selected != 1) fail("serial-qualified read-only image not enumerated");'
assert source.count(anchor)==1
source=source.replace(anchor,anchor+'''
    const char *expected = !strcmp(serial, "sdk-system") ? "vda" :
                           !strcmp(serial, "sdk-vendor") ? "vdb" :
                           !strcmp(serial, "sdk-sysprod") ? "vdc" : NULL;
    if (!expected || strcmp(name, expected)) fail("original fstab read-only disk ordering");''')
anchor='    if (selected != 1) fail("RAM-backed scratch data not enumerated");'
assert source.count(anchor)==1
source=source.replace(anchor,anchor+'\n    if (strcmp(name, "vdd")) fail("original fstab scratch data ordering");')
anchor='!option(buffer, "harmony.original_init_test=1") || !option(buffer, "enforcing=1")'
assert source.count(anchor)==1
source=source.replace(anchor,anchor+' || !option(buffer, "ohos.boot.hardware=hmos.emulator")')
anchor='    char *const environment[] = '
assert source.count(anchor)==1
source=source.replace(anchor,'    dprintf(1, "ORIGINAL_INIT038_LAYOUT_GUARDED original_fstab_order=1 original_hardware=1\\n");\n'+anchor)
source=source.replace('ORIGINAL_INIT037_','ORIGINAL_INIT038_')
payload='source='+repr(source)+'\n'+parent['payload'][parent['payload'].index('\nfrom pathlib import Path')+1:]
payload=payload.replace('baremetal-sdk-original-init-037','baremetal-sdk-original-init-038')
anchor="policy=dump('vendor.img'"
assert payload.count(anchor)==1
payload=payload.replace(anchor,"""fstab=dump('vendor.img','/etc/fstab.hmos.emulator','original-fstab')
fstab_rows=[line.split() for line in fstab.read_text().splitlines() if line.strip() and not line.lstrip().startswith('#')]
for device,target in [('vda','/usr'),('vdb','/vendor'),('vdc','/sys_prod'),('vdd','/data')]:
 row=next(row for row in fstab_rows if row[0]=='/dev/block/'+device and row[1]==target)
 assert row[2]=='ext4'
 assert ('ro' if target!='/data' else 'rw') in row[3].split(',')
"""+anchor)
compile(payload,'original-init-038-prepare','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)
