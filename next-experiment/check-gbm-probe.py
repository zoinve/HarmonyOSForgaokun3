"""Check the minimal GBM backend search-path repair."""
from pathlib import Path
import runpy

base = Path(__file__).resolve().parent
source = (base / 'payload-885/init.c').read_text()
fix = runpy.run_path(str(base / 'gbm-probe.py'))['gbm_probe']
result = fix(source)
assert '"GBM_BACKENDS_PATH=/system/lib64/lab-softpipe-167/gbm",NULL' in result
assert 'setenv("GBM_BACKENDS_PATH","/system/lib64/lab-softpipe-167/gbm",1);' in result
assert result.count('GBM_BACKENDS_PATH') == 2
assert 'GPU883_RAM_OVERLAY frontend_preserved=1 drawing_not_bypassed=1' in result
print('PASS: GBM path reaches product init and independent EGL probe')
