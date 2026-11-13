"""Exercise actual local bind views and error propagation in a disposable mount namespace."""
import subprocess
payload=r'''
from pathlib import Path
import ctypes,errno,subprocess,tempfile
ref=Path('/mnt/d/lab/HarmonyOSForMatebookego/references/L410-HarmonyOS-Adaptations/storage-hmdfs/storage_hmdfs_compat_shim.c')
with tempfile.TemporaryDirectory(prefix='native-local-storage-001-') as tmp:
 p=Path(tmp);so=p/'shim.so'
 subprocess.run(['gcc','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror',str(ref),'-o',str(so)],check=True)
 # subprocess namespace and its bind mounts die before the temporary tree is removed.
 code=r"""
import ctypes,errno,sys
from pathlib import Path
p=Path(sys.argv[1]);libc=ctypes.CDLL(None,use_errno=True)
assert libc.mount(None,b'/',None,(1<<18)|(1<<14),None)==0
shim=ctypes.CDLL(str(p/'shim.so'),use_errno=True)
shim.mount.argtypes=[ctypes.c_char_p,ctypes.c_char_p,ctypes.c_char_p,ctypes.c_ulong,ctypes.c_void_p]
src=p/'source';src.mkdir();(src/'proof').write_text('real backing data')
for name,views in [('account',['device_view/local','merge_view','cloud_merge_view']),('non_account',['merge_view']),('cloud',[''])]:
 target=p/name;target.mkdir()
 assert shim.mount(bytes(src),bytes(target),b'hmdfs',0,None)==0,(name,ctypes.get_errno())
 for view in views:
  q=target/view/'proof';assert q.read_text()=='real backing data'
  q.write_text('roundtrip');assert (src/'proof').read_text()=='roundtrip';q.write_text('real backing data')
bad=p/'unknown';bad.mkdir()
assert shim.mount(bytes(src),bytes(bad),b'hmdfs',0,None)==-1 and ctypes.get_errno()==errno.EINVAL
assert shim.mount(b'/definitely-missing-device',bytes(bad),b'ext4',0,None)==-1
assert not (bad/'proof').exists()
print('PASS real account/non_account/cloud bind views, write-through and non-HMDFS errors')
"""
 subprocess.run(['unshare','--mount','python3','-c',code,str(p)],check=True)
'''
if __name__=='__main__':
 raise SystemExit(subprocess.run(['wsl','-d','Debian','-u','root','--','python3','-'],input=payload,text=True,timeout=120).returncode)
