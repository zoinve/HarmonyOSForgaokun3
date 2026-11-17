'''Isolated Settings recovery using desktop173 runtime and a short ESP alias.'''
from pathlib import Path
import json
import runpy
import sys

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
REPORT=ROOT/'reports/commercial61-native-197-r1'
OPERATIONS=('install-commercial-native','run-commercial-native','retrieve-commercial-evidence','verify-commercial-return')
configure_local_transport=runpy.run_path(str(BASE/'commercial-workflow-173.py'))['configure_local_transport']

PREFLIGHT=r'''
def settings197_preflight():
 from pathlib import Path
 import hashlib,json,os,stat,subprocess
 def command(args):return subprocess.check_output(args,text=True,stderr=subprocess.PIPE,timeout=180)
 def digest(path):
  with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
 device='/dev/nvme0n1p4';mount=Path('/mnt/settings197-preflight')
 assert not mount.exists()
 identity=dict(line.split('=',1) for line in command(['blkid','-p','-o','export',device]).splitlines() if '=' in line)
 assert identity['UUID']=='00029cdd-1748-4d2f-b73b-8e8164922098' and identity['TYPE']=='ext4'
 assert not subprocess.run(['findmnt','-rn','-S',device],capture_output=True,text=True).stdout.strip()
 mount.mkdir(mode=0o700);mounted=False
 try:
  subprocess.run(['mount','-t','ext4','-o','ro,noload,nodev,nosuid,noexec',device,str(mount)],check=True,timeout=30);mounted=True
  assert mount.stat().st_dev==os.stat(device).st_rdev
  root=mount/'harmony-settings-data-197';data=root/'data.ext4'
  assert not root.is_symlink() and stat.S_IMODE(root.stat().st_mode)==0o700 and root.stat().st_uid==0
  info=data.stat()
  assert data.is_file() and not data.is_symlink() and info.st_nlink==1 and info.st_uid==0 and info.st_gid==0
  assert stat.S_IMODE(info.st_mode)==0o600 and info.st_size==8589934592 and info.st_blocks*512>=8589934592
  assert not command(['losetup','-j',str(data)]).strip()
  probe=dict(line.split('=',1) for line in command(['blkid','-p','-o','export',str(data)]).splitlines() if '=' in line)
  assert probe['TYPE']=='ext4' and probe['UUID']=='b8383c4f-844b-46cc-9d67-34a3745b3f1f'
  assert digest(data)=='f315f5adf08f31d1c99be3a3c11f23cf256a642b83e179d406cbf72e9abd36ce'
  check=subprocess.run(['e2fsck','-f','-n',str(data)],capture_output=True,timeout=180)
  assert check.returncode==0,'candidate must remain offline fsck clean'
  provision=json.loads((root/'provision.json').read_text())
  active=mount/'harmony-persistent-data-165/data.ext4'
  assert not active.is_symlink() and active.stat().st_size==8589934592
  assert digest(active)==provision['active165_before_sha256']==provision['active165_after_sha256']
 finally:
  if mounted:subprocess.run(['umount',str(mount)],check=True,timeout=60)
  mount.rmdir()
settings197_preflight()
'''


def source197(operation):
    assert operation in OPERATIONS
    source=(ROOT/'reports/commercial61-native-173'/(operation+'.generated.py')).read_text()
    for old,new in [('commercial61-native-173','commercial61-native-197'),
                    ('commercial-return-audit-173','commercial-return-audit-197'),
                    ('ordered_chain_equals_full_173','ordered_chain_equals_full_197'),
                    ('estimated173','estimated197'),
                    ('native persistent NVMe data diagnostics history and teardown 173','native isolated original Settings state recovery 197')]:
        source=source.replace(old,new)
    source=source.replace("/'reports/commercial61-native-197'", "/'reports/commercial61-native-197-r1'")
    source=source.replace('/home/zoinve/harmony-virgl-883/commercial61-native-197/',
                          '/home/zoinve/harmony-virgl-883/commercial61-native-197-r1/')
    if operation=='install-commercial-native':
        split="code='payload='"
        assert source.count(split)==1
        local,remote=source.split(split,1)
        remote=remote.replace("'commercial61-native-197/initrd.img'", "'set197.img'")
        remote=remote.replace("'initrd /commercial61-native-197/initrd.img'", "'initrd /set197.img'")
        old="dest=esp/'commercial61-native-197';entry="
        assert remote.count(old)==1
        remote=remote.replace(old,'dest=esp;entry=',1)
        old='assert not dest.exists() and not entry.exists()'
        assert remote.count(old)==1
        remote=remote.replace(old,"assert not (dest/'set197.img').exists() and not entry.exists()",1)
        assert remote.count('dest.mkdir()\n')==1
        remote=remote.replace('dest.mkdir()\n','',1).replace("dest/'initrd.img'","dest/'set197.img'")
        start=remote.index("old=(esp/'loader/entries/harmonyos-gpu-manual.conf').read_text()")
        anchor='assert estimated197<1800,estimated197\n'
        end=remote.index(anchor,start)+len(anchor)
        options=remote[start:end]
        remote=remote[:start]+remote[end:]
        anchor='assert not root.exists();root.mkdir()'
        assert remote.count(anchor)==1
        remote=remote.replace(anchor,options+PREFLIGHT+'assert not root.exists()',1)
        anchor="(root/'installation-journal.json').open('x')"
        assert remote.count(anchor)==1
        remote=remote.replace(anchor,"root.mkdir()\n"+anchor,1)
        source=local+split+remote
        source=source.replace('capture_output=True,timeout=400)','capture_output=True,timeout=900)')
    elif operation=='run-commercial-native':
        overlay=json.loads((REPORT/'overlay-result.json').read_text())
        check="from pathlib import Path\nimport hashlib\nassert hashlib.sha256(Path('/boot/efi/set197.img').read_bytes()).hexdigest()=="+repr(overlay['sha256'])+'\n'
        anchor='input=startcode,text=True'
        assert source.count(anchor)==1
        source=source.replace(anchor,'input='+repr(PREFLIGHT+check)+'+startcode,text=True',1)
        source=source.replace('capture_output=True,timeout=30)','capture_output=True,timeout=300)',1)
    elif operation=='retrieve-commercial-evidence':
        runs=[json.loads((ROOT/'reports/commercial61-native-173/runtime-evidence/retrieval-manifest.json').read_text())['run'],
              json.loads((ROOT/'reports/commercial61-native-175-compile-fix-1/early-return-inspection.json').read_text())['run']]
        anchor='if p.name not in ['
        assert source.count(anchor)==1
        source=source.replace(anchor,anchor+', '.join(repr(run) for run in runs)+', ',1)
    elif operation=='verify-commercial-return':
        source=source.replace("esp/'commercial61-native-197/initrd.img'", "esp/'set197.img'")
    return source


if __name__=='__main__':
    assert len(sys.argv)==2 and sys.argv[1] in (*OPERATIONS,'retain-entries')
    admission=json.loads((REPORT/'admission-test.json').read_text())
    assert admission and all(admission.values())
    provision=json.loads((ROOT/'reports/settings-data-deploy-198-r3/provision.json').read_text())
    assert provision['active165_unchanged'] and provision['lab_partition_unmounted']
    configure_local_transport()
    if sys.argv[1]=='retain-entries':
        path=BASE/'retain-latest-experiment-boot-entries-001.py'
        source=path.read_text()
        assert source.count('commercial[-2:]')==1
        source=source.replace('commercial[-2:]',
            "[p for p in commercial if p.name in {'commercial61-native-173.conf','commercial61-native-197.conf'}]",1)
        source=source.replace('assert all((entries/n).is_file() for n in keep)',
            "assert len(keep)==4 and all((entries/n).is_file() for n in keep)",1)
        exec(compile(source,str(path),'exec'),{'__name__':'__main__','__file__':str(path)})
    else:
        operation=sys.argv[1];source=source197(operation)
        assert source==(REPORT/(operation+'.generated.py')).read_text()
        exec(compile(source,operation,'exec'),{'__name__':'__main__','__file__':str(BASE/(operation+'-197.py'))})
