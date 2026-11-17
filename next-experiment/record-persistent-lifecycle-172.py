"""Record local-only lifecycle checks without touching the MateBook or old evidence."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

BASE = Path(__file__).resolve().parent
REPORT = BASE.parent / 'reports/persistent-lifecycle-172'

if __name__ == '__main__':
    assert os.geteuid() == 0 and not REPORT.exists()
    names = ['persistent-unmount-plan-172.h','persistent-data-172.h',
        'persistent-lifecycle-172.py','test-persistent-lifecycle-172.py',
        'persistent-data-166.h','build-commercial-native-168.py','build-commercial-native-166.py']
    before = {name: hashlib.sha256((BASE / name).read_bytes()).hexdigest() for name in names}
    REPORT.mkdir()
    env = dict(os.environ,HARMONY172_REAL_MOUNTS='1')
    proc = subprocess.run([sys.executable,str(BASE / 'test-persistent-lifecycle-172.py')],
        capture_output=True,text=True,timeout=180,env=env)
    (REPORT / 'tests.stdout').open('x').write(proc.stdout)
    (REPORT / 'tests.stderr').open('x').write(proc.stderr)
    after = {name: hashlib.sha256((BASE / name).read_bytes()).hexdigest() for name in names}
    result = dict(tests_exit=proc.returncode,input_hashes=before,inputs_unchanged=before==after,
        real_mount_namespace_tests_enabled=True,remote_target_accessed=False,
        native_boot_performed=False,native_storage_recurrence_prevention_verified=False,
        desktop_startup_fixed=False)
    (REPORT / 'result.json').open('x').write(json.dumps(result,indent=2))
    print(proc.stdout,end='')
    print(proc.stderr,end='',file=sys.stderr)
    assert proc.returncode == 0 and before == after
