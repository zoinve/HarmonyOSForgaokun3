"""Retain failed002 deployment; run the old-Mesa regression in fresh003 paths."""
from pathlib import Path
import runpy

source=runpy.run_path(str(Path(__file__).with_name('run-baremetal-fd-identity-probe-002.py')))['source']
for old,new in [('baremetal-fd-identity-probe-002','baremetal-fd-identity-probe-003'),
                ('fd-identity-transfer-002','fd-identity-transfer-003'),
                ('harmony-lab-fd-identity-probe-001','harmony-lab-fd-identity-probe-003'),
                ('FD_IDENTITY002','FD_IDENTITY003')]:
    assert old in source,old
    source=source.replace(old,new)
compile(source,'fd-identity003-regression','exec')
if __name__=='__main__':
    exec(compile(source,__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})
