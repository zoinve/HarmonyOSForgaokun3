"""Read-only extraction of completed 959 logs; validate every transferred file."""
from pathlib import Path
import hashlib
import json
import subprocess

base=Path(__file__).resolve().parent
out=base.parent/'reports/official-arm-evidence-959-verified'
assert not out.exists()
script=r'''
from pathlib import Path
import hashlib,json,subprocess
root=Path('/home/zoinve/.local/share/harmony-arm64-kvm-lab/official-arm-sdk-921/full-system-959')
result=json.loads((root/'result.json').read_text())
assert all(result[k] for k in ('readonly_inputs_unchanged','official_originals_unchanged','protected_userdata_original_unchanged'))
image=root/'userdata-permissive.img';out=root/'offline-evidence-verified';out.mkdir()
rows=[]
for folder in ('/log/faultlog/temp','/log/hilog','/log/faultlog/faultlogger'):
    r=subprocess.run(['debugfs','-n','-R','ls -p '+folder,str(image)],capture_output=True,text=True,check=True)
    assert 'Filesystem not open' not in r.stderr,r.stderr
    for line in r.stdout.splitlines():
        parts=line.split('/')
        if len(parts)<7:continue
        name=parts[5]
        if not name.endswith(('.json','.gz','.zip','.log')):continue
        assert Path(name).name==name and name not in ('.','..')
        dest=out/name;assert not dest.exists()
        r=subprocess.run(['debugfs','-n','-R',f'dump {folder}/{name} {dest}',str(image)],capture_output=True,text=True,check=True)
        assert dest.is_file(),r.stderr
        rows.append(dict(name=name,size=dest.stat().st_size,sha256=hashlib.sha256(dest.read_bytes()).hexdigest()))
assert len(rows)>=5
(out/'evidence-manifest.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows,indent=2))
'''
r=subprocess.run(['ssh','matebook','sudo -n python3 -'],input=script,text=True,capture_output=True,check=True)
subprocess.run(['scp','-r','matebook:/home/zoinve/.local/share/harmony-arm64-kvm-lab/official-arm-sdk-921/full-system-959/offline-evidence-verified',str(out)],check=True)
rows=json.loads((out/'evidence-manifest.json').read_text())
for row in rows:
    p=out/row['name']
    assert p.stat().st_size==row['size'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
print(json.dumps(dict(evidence_files_verified=len(rows),userdata_modified=False)))
