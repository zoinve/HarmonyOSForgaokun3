"""Wait for original init's device preparation, never relabel or bypass its policy."""
from pathlib import Path
import runpy
import subprocess

parent=runpy.run_path(str(Path(__file__).with_name('prepare-baremetal-sdk-original-init-039.py')))
source=parent['source']
changes={
 '    require(fd >= 0, "open enforcing-policy Binder ping caller");':'''    if (fd < 0 && (errno == ENOENT || errno == EACCES)) {
        dprintf(1, "ORIGINAL_INIT040_BINDER_NOT_READY stage=open errno=%d\\n", errno);
        return 0;
    }
    require(fd >= 0, "open enforcing-policy Binder ping caller");''',
 '    require(mapping != MAP_FAILED, "bounded Binder caller mapping");':'''    if (mapping == MAP_FAILED && (errno == EACCES || errno == ENOENT)) {
        int saved = errno; close(fd);
        dprintf(1, "ORIGINAL_INIT040_BINDER_NOT_READY stage=mmap errno=%d\\n", saved);
        return 0;
    }
    require(mapping != MAP_FAILED, "bounded Binder caller mapping");'''
}
for old,new in changes.items():
    assert source.count(old)==1;source=source.replace(old,new)
source=source.replace('ORIGINAL_INIT039_','ORIGINAL_INIT040_')
payload='source='+repr(source)+'\n'+parent['payload'][parent['payload'].index('\nfrom pathlib import Path')+1:]
payload=payload.replace('baremetal-sdk-original-init-039','baremetal-sdk-original-init-040')
compile(payload,'original-init-040-prepare','exec')
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=180)
    raise SystemExit(r.returncode)
