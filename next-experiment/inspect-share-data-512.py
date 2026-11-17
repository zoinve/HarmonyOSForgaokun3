"""Read only selected P2P log counters from experimental data197 after return."""
from collections import Counter
from pathlib import Path
import inspect
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    'group_started': r'\bP2P-GROUP-STARTED\b',
    'group_removed': r'\bP2P-GROUP-REMOVED\b',
    'group_formation_failure': r'\bP2P-GROUP-FORMATION-FAILURE\b',
    'wpa_key_negotiation_completed': r'WPA: Key negotiation completed',
    'driver_initialization_failure': r'Failed to initialize driver interface',
    'driver_mode_failure': r'Could not configure driver mode',
    'p2p_initialization_failure': r'Failed to init P2P|Failed to enable P2P Device',
    'control_initialization_failure': r'Failed to initialize control interface',
    'resource_busy': r'Device or resource busy',
    'rfkill_blocked': r'rfkill:.*blocked',
    'unknown_command': r'UNKNOWN COMMAND',
    'nl80211_failure_word': r'nl80211:.*(?:Could not|Failed to|failed)',
}
GROUP_KINDS = {'register','create','connect-gc','configure-go-ip','dhcp-range','dhcp-name',
    'dhcp-start','dhcp-stop','connection-event','configure-gc-ip','release-gc-ip',
    'shared-reference','local-network-route','subnet-conflict','allocate-gc-ip',
    'current-group-text-lens','current-group-peer-lens'}


def scan(stream):
    counts = Counter()
    group = Counter()
    total = 0
    for raw in stream:
        total += len(raw)
        if total > 16 * 1024**2: break
        line = raw.decode(errors='replace')
        for label, pattern in PATTERNS.items():
            if re.search(pattern,line): counts[label] += 1
        match = re.fullmatch(r'\d+\.\d+ ([a-z-]+) a=-?\d+ b=-?\d+ result=(-?\d+)\s*',line)
        if match and match[1] in GROUP_KINDS:
            group[(match[1],int(match[2]))] += 1
    return dict(events=dict(counts),group_results=[dict(kind=kind,result=result,count=count)
        for (kind,result),count in sorted(group.items())],bounded_bytes=min(total,16*1024**2),
        cumulative_log_not_proven_run_isolated=True,raw_peer_data_exported=False,
        file_transfer_verified=False)


REMOTE = r'''
import collections,re
Counter=collections.Counter
lab=Path('/mnt/harmony-share-lab-512')
data=Path('/mnt/harmony-share-data-512')
for directory in [lab,data]:
 assert not directory.exists()
 directory.mkdir(mode=0o700)
loop=None
lab_mounted=data_mounted=False
try:
 subprocess.run(['mount','-t','ext4','-o','ro,noload','/dev/nvme0n1p4',str(lab)],check=True,timeout=30)
 lab_mounted=True
 source=lab/'harmony-settings-data-197/data.ext4'
 assert source.resolve().is_relative_to(lab) and stat.S_ISREG(source.lstat().st_mode)
 assert source.stat().st_size==8589934592
 loop=command(['losetup','--find','--show','--read-only',str(source)]).strip()
 assert re.fullmatch(r'/dev/loop\d+',loop)
 assert command(['blkid','-p','-s','UUID','-o','value',loop]).strip()=='b8383c4f-844b-46cc-9d67-34a3745b3f1f'
 subprocess.run(['mount','-t','ext4','-o','ro,noload',loop,str(data)],check=True,timeout=30)
 data_mounted=True
 rows={}
 for label,name in [('supplicant','local/tmp/l410_p2p_ctrl/supplicant.log'),
                    ('original_bridge','local/tmp/l410-wifi-compat-v2/p2p-group-v11.log')]:
  path=data/name
  assert path.resolve().is_relative_to(data)
  try: fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC)
  except FileNotFoundError:
   rows[label]=dict(available=False)
   continue
  with os.fdopen(fd,'rb') as stream:
   metadata=os.fstat(stream.fileno())
   assert stat.S_ISREG(metadata.st_mode)
   rows[label]=dict(available=True,file_bytes=metadata.st_size,analysis=scan(stream))
 result=dict(selected_logs=rows,data197_readonly=True,noload=True,
  active165_accessed=False,raw_credentials_or_peer_identity_exported=False,
  huawei_share_file_transfer_verified=False)
finally:
 if data_mounted:subprocess.run(['umount',str(data)],check=True,timeout=30)
 if loop:subprocess.run(['losetup','-d',loop],check=True,timeout=30)
 if lab_mounted:subprocess.run(['umount',str(lab)],check=True,timeout=30)
 for directory in [data,lab]:directory.rmdir()
assert not subprocess.run(['findmnt','-rn','-S','/dev/nvme0n1p4'],capture_output=True,text=True).stdout.strip()
print(json.dumps(result,indent=2))
'''


if __name__ == '__main__':
    report = ROOT / 'reports/commercial61-native-502'
    assert json.loads((report / 'boot-observation-506.json').read_text())['returned']
    output = report / 'share-data-analysis-512.json'
    assert not output.exists()
    workflow = runpy.run_path(str(ROOT / 'next-experiment/settings-workflow-254.py'))
    code = workflow['GUARD'] + '\nfrom collections import Counter\nimport re\n'
    code += 'PATTERNS=' + repr(PATTERNS) + '\nGROUP_KINDS=' + repr(GROUP_KINDS) + '\n'
    code += inspect.getsource(scan) + REMOTE
    text = workflow['remote'](code,timeout=180)
    output.open('x').write(text)
    print(text)
