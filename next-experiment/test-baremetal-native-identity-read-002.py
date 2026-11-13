"""Compile and exercise the actual legacy-Binder probe's pre-side-effect refusal."""
from pathlib import Path
import subprocess

file=Path(__file__).with_name('baremetal-native-identity-read-002.c')
assert file.exists(), 'missing legacy-Binder and enforcing read probe'
payload='source='+repr(file.read_text())+'\n'+r'''
from pathlib import Path
import subprocess,tempfile
with tempfile.TemporaryDirectory(prefix='native-identity-read002-') as directory:
 p=Path(directory);(p/'probe.c').write_text(source)
 subprocess.run(['cc','-O2','-Wall','-Wextra','-Werror',str(p/'probe.c'),'-o',str(p/'probe')],check=True)
 r=subprocess.run([str(p/'probe')],capture_output=True,text=True,timeout=5)
 assert r.returncode==77 and 'requires diagnostic kernel and opt-in' in r.stderr,(r.returncode,r.stdout,r.stderr)
 print('PASS: actual legacy-Binder read probe refuses host before device/mount operations')
'''
if __name__=='__main__':
 result=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=40)
 raise SystemExit(result.returncode)
