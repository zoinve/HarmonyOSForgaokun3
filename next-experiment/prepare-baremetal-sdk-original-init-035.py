"""Correct only guest disk discovery; numbered 034 evidence remains immutable."""
from pathlib import Path
import runpy
import subprocess

source=Path(__file__).with_name('baremetal-sdk-original-init-034.c').read_text()
header=Path(__file__).with_name('baremetal-sdk-disk-selection-035.h').read_text()
source=source.replace('static void readonly_image(const char *name, const char *target)',
    header+'\nstatic void readonly_image(const char *serial, unsigned long long sectors, const char *target)')
start=source.index('    char path[128], identity[128];',source.index('static void readonly_image'))
end=source.index('    struct stat st;',start)
source=source[:start]+'''    char name[32], path[128], identity[128];
    int selected = 0;
    for (unsigned i = 0; i < 100; ++i) {
        selected = sdk_select_disk_035("/sys/class/block", serial, sectors, name, sizeof(name));
        if (selected < 0) fail("unsafe duplicate or wrong capacity image identity");
        if (selected == 1) break;
        usleep(20000);
    }
    if (selected != 1) fail("serial-qualified read-only image not enumerated");
    snprintf(path, sizeof(path), "/sys/class/block/%s/dev", name);
    unsigned major_number = 0, minor_number = 0;
    if (read_path(path, identity, sizeof(identity)) <= 0 ||
        sscanf(identity, "%u:%u", &major_number, &minor_number) != 2) fail("image major/minor identity");
    snprintf(path, sizeof(path), "/dev/%s", name);
'''+source[end:]
for old,new in [('readonly_image("vda", "/usr")','readonly_image("sdk-system", 7168000, "/usr")'),
                ('readonly_image("vdb", "/vendor")','readonly_image("sdk-vendor", 204800, "/vendor")'),
                ('readonly_image("vdc", "/sys_prod")','readonly_image("sdk-sysprod", 2048000, "/sys_prod")')]:
    assert source.count(old)==1;source=source.replace(old,new)
source=source.replace('ORIGINAL_INIT034_','ORIGINAL_INIT035_')
parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-034.py')))['payload']
payload='source='+repr(source)+'\n'+parent[parent.index('\nfrom pathlib import Path')+1:]
payload=payload.replace('baremetal-sdk-original-init-034','baremetal-sdk-original-init-035')
compile(payload,'original-init-035-prepare','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)
