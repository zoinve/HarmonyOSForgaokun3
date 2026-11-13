"""Require an actual independently linked adapter/composer before staging."""
from pathlib import Path
import subprocess
base=Path(__file__).resolve().parent
assert (base/'build-native-cursor-032.py').is_file(),'missing real adapter/composer build'
code=r'''
from pathlib import Path
import json,hashlib,subprocess
r=Path('/home/zoinve/harmony-virgl-883/native-cursor-032-r2')
m=json.loads((r/'result.json').read_text())
for n,h in m['sha256'].items():assert hashlib.sha256((r/n).read_bytes()).hexdigest()==h
assert m['original_adapter_sha256']=='03e64bcecc882791855ec26840cfbfc8c4763e40e0e1612a677fd0d52b335d3e'
assert m['original_composer_unchanged'] and m['input_injection']==False
for n in ['libcursor_drawing_adapter.z.so','libdisplay_composer_vdi_impl.z.so']:
 s=subprocess.check_output(['aarch64-linux-gnu-readelf','-h',str(r/n)],text=True)
 assert 'AArch64' in s
print('PASS independently linked AArch64 adapter/composer, original artifacts retained; runtime pending')
'''
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=code,text=True).returncode)
