"""Reuse live-captured render-only isolation for the extracted-method GPU experiment."""
from pathlib import Path
import runpy

base=Path(__file__).resolve().parent
source=(base/'run-baremetal-freedreno-ipc-002.py').read_text()
for old,new in [('baremetal-freedreno-ipc-package-002','baremetal-composer-probe-package-002'),
                ('baremetal-freedreno-ipc-run-002','baremetal-composer-probe-run-002'),
                ('harmony-lab-freedreno-ipc','harmony-lab-composer-contract'),
                ("len(expected['files'])==9","len(expected['files'])==10")]:
    assert old in source,old
    source=source.replace(old,new)
anchor="compile(source,'ipc002-render-only-remote','exec')"
assert source.count(anchor)==1
source=source.replace(anchor,"""source=source.replace('harmony-lab-freedreno-ipc','harmony-lab-composer-contract').replace('IPC002_','COMPOSER001_')
compile(source,'composer002-render-only-remote','exec')""")
anchor="    (out/'result.json').write_text"
assert source.count(anchor)==1
source=source.replace(anchor,"""    report['extracted_composer_contract_gpu_verified']=report['cross_process_gpu_execution_verified'] and 'COMPOSER001_CONTRACT actual_reference_methods=1 caller_fds_closed=1 held_fd_closed=1 no_init_display=1 no_commit=1' in text
    report['full_composer_hdi_verified']=False
"""+anchor)
compile(source,'composer002-operational','exec')
if __name__=='__main__':
    exec(compile(source,__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})
