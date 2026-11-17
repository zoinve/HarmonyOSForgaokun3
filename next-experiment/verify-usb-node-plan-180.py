"""Preserve test results for the unintegrated USB node planner."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent

if __name__ == '__main__':
    report=ROOT/'reports/usb-node-plan-180'
    assert not report.exists(), 'preserve numbered evidence'
    report.mkdir()
    sources=['usb-node-plan-180.h','test-usb-node-plan-180.py','usb-readonly-175.h',
             'usb-readonly-176.h','native-usb-storage-174.h']
    result=dict(source_sha256={name:hashlib.sha256((BASE/name).read_bytes()).hexdigest() for name in sources},
                tests=[],target_modified=False,native_runtime_integrated=False,
                nodes_created=False,media_mounted=False,native_storage_acceptance=False)
    for name in ['test-usb-node-plan-180.py','test-usb-readonly-175.py',
                 'test-usb-readonly-176.py','test-native-usb-storage-174.py']:
        proc=subprocess.run(['python3',str(BASE/name)],capture_output=True,text=True,timeout=120)
        (report/(name+'.stdout')).open('x').write(proc.stdout)
        (report/(name+'.stderr')).open('x').write(proc.stderr)
        counts=re.findall(r'Ran (\d+) tests?',proc.stderr)
        row=dict(name=name,returncode=proc.returncode,test_count=int(counts[-1]) if counts else 0)
        result['tests'].append(row)
        if proc.returncode or not row['test_count']:
            (report/'failure.json').open('x').write(json.dumps(result,indent=2))
            raise SystemExit('planner verification failed; preserve evidence and do not integrate')
    (report/'result.json').open('x').write(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
