"""Recover journal metadata only on a new sparse clone, never on the original device."""
from pathlib import Path
import subprocess,json
root=Path(__file__).resolve().parents[1]/'reports/commercial61-native-004'
code=r'''
from pathlib import Path
import subprocess,json,shutil,os
work=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/commercial61-evidence-recovery-004')
assert not work.exists();assert shutil.disk_usage(work.parent).free>2*1024**3
assert subprocess.run(['findmnt','-rn','-S','/dev/nvme0n1p4'],capture_output=True).returncode!=0
work.mkdir();clone=work/'metadata-clone.img'
commands=[['e2image','-r','/dev/nvme0n1p4',str(clone)],['e2fsck','-y','-E','journal_only',str(clone)]]
results=[]
for i,cmd in enumerate(commands):
 r=subprocess.run(cmd,capture_output=True,timeout=240)
 (work/f'command-{i}.stdout').open('xb').write(r.stdout);(work/f'command-{i}.stderr').open('xb').write(r.stderr)
 results.append(dict(command=cmd,exit_code=r.returncode,stdout=r.stdout.decode(errors='replace'),stderr=r.stderr.decode(errors='replace')))
 assert r.returncode in ([0] if i==0 else [0,1]),results
result=dict(work=str(work),clone=str(clone),allocated_bytes=clone.stat().st_blocks*512,bytes=clone.stat().st_size,commands=results,original_partition_replayed=False,clone_file_data_not_authoritative=True)
(work/'result.json').open('x').write(json.dumps(result,indent=2));print(json.dumps(result))
'''
r=subprocess.run(['ssh','matebook','sudo -n python3 -'],input=code,text=True,capture_output=True,timeout=550)
(root/'metadata-clone.stdout').open('x').write(r.stdout);(root/'metadata-clone.stderr').open('x').write(r.stderr)
assert r.returncode==0,r.stderr
result=json.loads(r.stdout);(root/'metadata-clone-result.json').open('x').write(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
