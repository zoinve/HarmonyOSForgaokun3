"""Execute the actual handoff helper outside PID1: it must refuse before mounting."""
from pathlib import Path
import subprocess

source=Path(__file__).with_name('baremetal-sdk-original-init-034.c').read_text()
payload='source='+repr(source)+'\n'+r'''
from pathlib import Path
import subprocess,tempfile
with tempfile.TemporaryDirectory(prefix='original-init034-',dir='/home/zoinve/harmony-virgl-883') as d:
 p=Path(d);(p/'init.c').write_text(source)
 subprocess.run(['cc','-O2','-Wall','-Wextra','-Werror',str(p/'init.c'),'-o',str(p/'init')],check=True)
 r=subprocess.run([str(p/'init')],capture_output=True,text=True,timeout=5)
 assert r.returncode==77,(r.returncode,r.stdout,r.stderr)
 assert 'ORIGINAL_INIT034_REFUSED' in r.stderr
 print('PASS: actual C helper refuses non-PID1 before any mount/device action')
'''
if __name__=='__main__':
    r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=60)
    raise SystemExit(r.returncode)
