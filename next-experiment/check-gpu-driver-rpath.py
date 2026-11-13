"""Check the actual staged driver DSOs, not merely the launcher environment."""
import subprocess
import sys

script = r'''
from pathlib import Path
import subprocess
root=Path(ROOT)/'gpu883-libs'
required=['gbm/dri_gbm.so','libgallium-25.0.1.so']
for relative in required:
 p=root/relative
 assert p.is_file()
 paths=subprocess.check_output(['patchelf','--print-rpath',str(p)],text=True).strip().split(':')
 assert '/system/lib64/lab-softpipe-167' in paths,(relative,paths)
 assert not any('lab-virgl883' in x for x in paths),(relative,paths)
print('PASS: real GBM backend and Gallium dependencies use the mounted private directory')
'''.replace('ROOT', repr(sys.argv[1]))
subprocess.run(['wsl','-d','Debian','--','python3','-'],input=script,text=True,check=True)
