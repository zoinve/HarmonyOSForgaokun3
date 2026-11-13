"""Require a real compatible ashmem module, not a success stub."""
import subprocess
payload=r'''
from pathlib import Path
import json,hashlib,subprocess
r=Path('/home/zoinve/harmony-virgl-883/native-ashmem-module-001')
assert (r/'result.json').exists(),'native ashmem ABI module missing'
d=json.loads((r/'result.json').read_text());p=r/'hmos_ashmem.ko'
assert hashlib.sha256(p.read_bytes()).hexdigest()==d['module_sha256']
info=subprocess.check_output(['modinfo',str(p)],text=True)
assert '7.1.0-rc3-gaokun3-el2' in info
s=(r/'hmos_ashmem.c').read_text()
for x in ['shmem_file_setup','vfs_mmap_prepare','vfs_fallocate','-EPERM','-ENOTTY','module_misc_device']:
 assert x in s,x
assert d['reference_sources_unchanged'] and not d['loaded_in_ubuntu']
print(json.dumps(d,indent=2))
'''
if __name__=='__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)
