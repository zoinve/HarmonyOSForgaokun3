"""Verify reference namespace body unchanged and commercial argv preserved."""
from pathlib import Path
import runpy,subprocess
b=Path(__file__).resolve().parent
assert (b/'commercial-reference-namespace-036.py').exists(),'missing reference namespace adapter'
p=runpy.run_path(str(b/'commercial-reference-namespace-036.py'))
source=p['source']()
original=p['REFERENCE'].read_text()
assert source[source.index('int main('):]==original[original.index('int main('):]
assert 'libmali' not in source and 'libappspawn_helper.z.so' in source
assert 'setuid(' not in source and 'setcon(' not in source
old=b.parent/'reports/commercial61-native-035/matebook-appspawn-launcher.sh'
assert old.exists(),'locate saved original launcher before deployment'
launcher=p['launcher'](old.read_text())
assert '--sandbox-switch on' in launcher
assert '/system/bin/aurora/appspawn-reference-namespace' in launcher
assert '/vendor/lib64/passthrough /system/bin/appspawn' in launcher
remote='import subprocess,tempfile\nfrom pathlib import Path\nsource='+repr(source)+'''
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'test.c').write_text(source)
 subprocess.run(['cc','-Wall','-Wextra','-Werror',str(p/'test.c'),'-o',str(p/'test')],check=True)
 r=subprocess.run([str(p/'test')],capture_output=True,text=True)
 assert r.returncode==2 and 'usage:' in r.stderr
'''
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=remote,text=True,check=True)
print('PASS: reference namespace main byte-identical; commercial sandbox argv retained')
