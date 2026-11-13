"""Execute the real policy probe's host refusal, without mounting or loading policy."""
from pathlib import Path
import subprocess

path=Path(__file__).with_name('baremetal-selinux-load-013.c')
assert path.exists(), 'SELinux probe is not implemented'
payload='source='+repr(path.read_text())+'\n'+r'''
from pathlib import Path
import subprocess,tempfile
with tempfile.TemporaryDirectory(prefix='selinux-load-refusal-') as directory:
 p=Path(directory);(p/'init.c').write_text(source)
 subprocess.run(['cc','-O2','-Wall','-Wextra','-Werror',str(p/'init.c'),'-o',str(p/'probe')],check=True)
 r=subprocess.run([str(p/'probe')],text=True,capture_output=True,timeout=5)
 assert r.returncode==77 and 'requires isolated PID 1' in r.stderr,(r.returncode,r.stdout,r.stderr)
 print('PASS: actual SELinux probe refuses non-PID1 execution before mounts or policy operations')
'''
if __name__=='__main__':
 r=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=30)
 raise SystemExit(r.returncode)
