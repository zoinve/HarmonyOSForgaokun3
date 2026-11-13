"""Fresh003 deployment of the private extracted-method experiment, without display changes."""
from pathlib import Path
import runpy

source=runpy.run_path(str(Path(__file__).with_name('run-baremetal-composer-probe-002.py')))['source']
source=source.replace('baremetal-composer-probe-package-002','baremetal-composer-probe-package-003').replace('baremetal-composer-probe-run-002','baremetal-composer-probe-run-003')
source=source.replace('harmony-lab-composer-contract-transfer-002','harmony-lab-composer-contract-transfer-003')
anchor="compile(source,'composer002-render-only-remote','exec')"
assert source.count(anchor)==1
source=source.replace(anchor,"source=source.replace('harmony-lab-composer-contract-002','harmony-lab-composer-contract-003').replace('harmony-lab-composer-contract-transfer-002','harmony-lab-composer-contract-transfer-003').replace('harmony-lab-composer-contract-sandbox-002','harmony-lab-composer-contract-sandbox-003').replace('harmony-lab-composer-contract-probe-002','harmony-lab-composer-contract-probe-003')\n"+anchor)
compile(source,'composer003-operational','exec')
if __name__=='__main__':
    exec(compile(source,__file__,'exec'),{'__file__':__file__,'__name__':'__main__'})
