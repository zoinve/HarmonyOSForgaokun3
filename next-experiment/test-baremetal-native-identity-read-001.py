"""Run the real native read-only probe's refusal path, without device access."""
from pathlib import Path
import subprocess

source=Path(__file__).with_name('baremetal-native-identity-read-001.c').read_text()
payload='source='+repr(source)+'\n'+r'''
from pathlib import Path
import subprocess,tempfile
with tempfile.TemporaryDirectory(prefix='native-identity-read-test-') as directory:
 p=Path(directory);(p/'probe.c').write_text(source)
 subprocess.run(['cc','-O2','-Wall','-Wextra','-Werror',str(p/'probe.c'),'-o',str(p/'probe')],check=True)
 r=subprocess.run([str(p/'probe')],capture_output=True,text=True,timeout=5)
 assert r.returncode==77 and 'requires diagnostic kernel and opt-in' in r.stderr,(r.returncode,r.stdout,r.stderr)
 print('PASS: real read-only probe refuses the host before any device or mount operation')
'''
if __name__=='__main__':
    result=subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=30)
    raise SystemExit(result.returncode)
