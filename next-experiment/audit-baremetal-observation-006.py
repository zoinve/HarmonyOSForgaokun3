"""Run exact generated shell commands on ARM64, with isolated filesystem fixtures."""
from pathlib import Path
import ast
import hashlib
import json
import re
import runpy
import subprocess

base = Path(__file__).resolve().parent
report = base.parent / 'reports/baremetal-observation-006-command-audit.json'
assert not report.exists()
source = (base / 'baremetal-diagnostic-init.c').read_text()
for name in ('storage-002', 'board-003', 'deadline-004', 'display-005', 'observation-006'):
    source = runpy.run_path(str(base / ('baremetal-diagnostic-' + name + '.py')))['build_source'](source)


def shell_array(name):
    block = re.search(r'char \*' + name + r'\[\] = \{(.*?)NULL\};', source, re.S)[1]
    strings = [ast.literal_eval(s) for s in re.findall(r'"(?:[^"\\]|\\.)*"', block)]
    assert strings[:3] == ['/bin/busybox', 'sh', '-c']
    return ''.join(strings[3:])


payload = 'observe=' + repr(shell_array('observe')) + '\nbindings=' + repr(shell_array('bindings')) + '\n' + r'''
from pathlib import Path
import hashlib,json,subprocess,tempfile,time,threading
checks=[]
with tempfile.TemporaryDirectory(prefix='harmony-observation-006-',dir='/run') as tmp:
    root=Path(tmp);(root/'dev/dri').mkdir(parents=True);(root/'sys/class/drm/card0').mkdir(parents=True)
    card=root/'dev/dri/card0'
    def invoke(label):
        start=time.monotonic()
        r=subprocess.run(['/bin/busybox','sh','-c',observe,'observation-fixture',str(root)],capture_output=True,text=True,timeout=8)
        row=dict(case=label,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr,elapsed_seconds=time.monotonic()-start)
        checks.append(row);return row
    # Merely naming a regular file card0 must not manufacture a DRM-node success.
    card.write_text('not a device')
    row=invoke('regular-file-not-drm');assert row['returncode']==124 and 'DRM_NODE_NOT_OBSERVED' in row['stdout'] and row['elapsed_seconds']<8,row
    card.unlink();card.symlink_to('/dev/null')
    row=invoke('existing-character-node');assert row['returncode']==0 and row['elapsed_seconds']<1 and 'DRM_NODE_OBSERVED_NOT_DISPLAY_PROOF' in row['stdout'],row
    card.unlink()
    worker=threading.Thread(target=lambda:(time.sleep(0.4),card.symlink_to('/dev/null')));worker.start()
    try:row=invoke('node-appears-later')
    finally:worker.join()
    assert row['returncode']==0 and 0.25<=row['elapsed_seconds']<2,row
r=subprocess.run(['/bin/busybox','sh','-c',bindings],capture_output=True,text=True,timeout=5)
assert r.returncode==0 and 'BINDING_SNAPSHOT_COMPLETE_NOT_READINESS' in r.stdout,(r.returncode,r.stderr)
print(json.dumps(dict(boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
    observe_command_sha256=hashlib.sha256(observe.encode()).hexdigest(),checks=checks,
    binding_command_sha256=hashlib.sha256(bindings.encode()).hexdigest(),binding_stdout=r.stdout,binding_stderr=r.stderr,
    modules_loaded=False,boot_entries_modified=False,reboot_requested=False,physical_display_verified=False)))
'''
result = subprocess.run(['ssh', '-o', 'ConnectTimeout=3', 'matebook', 'sudo -n python3 -'],
                        input=payload, capture_output=True, text=True, timeout=35)
assert result.returncode == 0, result.stderr or result.stdout
record = json.loads(result.stdout)
record['generated_c_sha256'] = hashlib.sha256(source.encode()).hexdigest()
report.write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({k: v for k, v in record.items() if k not in ('binding_stdout', 'binding_stderr')}, indent=2))
