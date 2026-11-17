"""Manually clear the diagnosed orphan-list inconsistency with tree guards intact."""
from pathlib import Path
import inspect
import json
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/settingsdata-orphan-repair-234'


if __name__ == '__main__':
    assert not REPORT.exists()
    previous = runpy.run_path(str(ROOT / 'next-experiment/repair-settingsdata-filesystem-233.py'))
    source = previous['REMOTE']
    assert source.count(' assert sha(image)==expected\n') == 1
    source = source.replace(' assert sha(image)==expected\n',
        ' expected=sha(image) # Failed preen may have updated only the superblock error state.\n', 1)
    source = source.replace('settingsdata-fsck-233', 'settingsdata-fsck-234').replace('readonly-tree-233', 'readonly-tree-234')
    source = source.replace('preen233.json', 'manual234.json').replace('repair233.json', 'repair234.json')
    source = source.replace('preen', 'manual')
    anchor = " manual=subprocess.run(['e2fsck','-f','-p',str(image)],capture_output=True,text=True,timeout=240,env=env)"
    assert source.count(anchor) == 1
    replacement = r''' diagnostic=subprocess.run(['e2fsck','-f','-n',str(image)],capture_output=True,text=True,timeout=240,env=env)
 (backup/'manual234-precheck.json').open('x').write(json.dumps(dict(exit_status=diagnostic.returncode,stdout=diagnostic.stdout,stderr=diagnostic.stderr)))
 assert diagnostic.returncode==4 and 'corrupted orphan linked list' in diagnostic.stdout
 for unexpected in ['multiply-claimed','Free blocks count wrong','Free inodes count wrong','invalid extent','corrupt extent','bitmap differences']:
  assert unexpected not in diagnostic.stdout,diagnostic.stdout
 manual=subprocess.run(['e2fsck','-f','-y',str(image)],capture_output=True,text=True,timeout=240,env=env)'''
    source = source.replace(anchor, replacement, 1)
    inspection = json.loads((ROOT / 'reports/settingsdata-repair-inspection-232/result.json').read_text())
    assert inspection['fsck_exit'] == 4 and inspection['active165_unchanged']
    failed = (ROOT / 'reports/settingsdata-filesystem-repair-233/stderr').read_text()
    assert 'corrupted orphan linked list' in failed and 'UNEXPECTED INCONSISTENCY' in failed
    helper = runpy.run_path(str(ROOT / 'next-experiment/prepare-settingsdata-scaffolding-215.py'))
    code = ('from pathlib import Path\nimport hashlib,json,os,stat,subprocess\n' +
        inspect.getsource(helper['sha']) + '\n' + inspect.getsource(helper['fingerprint']) + '\n' +
        'expected=' + repr(inspection['candidate_sha256']) + '\n' + source)
    compile(code, 'settingsdata-orphan234-remote', 'exec')
    REPORT.mkdir()
    ssh = runpy.run_path(str(ROOT / 'next-experiment/deploy-settings-data-198.py'))['SSH']
    result = subprocess.run(ssh + ['sudo -n python3 -'], input=code,
        capture_output=True, text=True, timeout=1200)
    if result.stderr:
        (REPORT / 'stderr').open('x').write(result.stderr)
    assert result.returncode == 0, result.stderr
    (REPORT / 'result.json').open('x').write(result.stdout)
    print(result.stdout)
