"""Explicit user authorization supersedes archiving: delete only old 941/944/947/949 modified system images."""
from pathlib import Path
import argparse
import json
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
CHECKS = runpy.run_path(str(BASE/'archive-historical-images-20261112.py'))['PAYLOAD'].split('rows = JOB')[0]
DELETE = r'''
root=Path(JOB['root'])
report=root/'obsolete-image-deletion-20261112.json'
assert root.is_dir() and not root.is_symlink() and not report.exists()
targets=[]
evidence={}
for row in JOB['rows']:
    p=Path(row['path'])
    assert p.parent.parent==root and p.name=='system-graphics.img'
    assert p.parent.name in JOB['directories']
    allowed=[p,p.with_suffix('.img.gz'),p.with_suffix('.img.gz.partial')]
    for q in allowed:
        if q.exists():
            safe(q);unused(q)
            if q==p: assert sha(q)==row['sha256'], ('unexpected original bytes',str(q))
            targets.append(q)
    for q in p.parent.rglob('*'):
        if q.is_file() and q not in allowed and not q.is_symlink():
            evidence[str(q)]=sha(q)
assert targets
data=dict(root=str(root),free_before=shutil.disk_usage(root).free,
          user_authorized_direct_deletion=True,archives_not_retained=True,
          targets=[str(p) for p in targets],deleted=[],evidence_sha256=evidence)
if APPLY:
    for p in targets:
        safe(p);unused(p)
        entry=dict(path=str(p),bytes=p.stat().st_size,allocated_bytes=p.stat().st_blocks*512)
        p.unlink();assert not p.exists()
        data['deleted'].append(entry)
        report.write_text(json.dumps(data,indent=2))
    assert all(sha(Path(p))==digest for p,digest in evidence.items())
    data['sibling_evidence_unchanged']=True
data['free_after']=shutil.disk_usage(root).free
if APPLY:report.write_text(json.dumps(data,indent=2))
print(json.dumps(data))
'''


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host',choices=['wsl','matebook'],required=True)
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    if args.host=='wsl':
        root='/home/zoinve/harmony-virgl-883';prefix='official-system'
        command=['wsl','-d','Debian','-u','root','--','python3','-']
    else:
        root='/home/zoinve/.local/share/harmony-arm64-kvm-lab/official-arm-sdk-921';prefix='full-system'
        command=['ssh','matebook','sudo -n python3 -']
    rows=[];directories=[]
    for n in [941,944,947,949]:
        m=json.loads((BASE/f'official-system-{n}/manifest.json').read_text())
        row=dict(next(x for x in m['images'] if Path(x['path']).name=='system-graphics.img'))
        directories.append(f'{prefix}-{n}')
        row['path']=f'{root}/{prefix}-{n}/system-graphics.img';rows.append(row)
    job=dict(root=root,rows=rows,directories=directories)
    r=subprocess.run(command,input=CHECKS+'\nJOB='+repr(job)+'\nAPPLY='+repr(args.apply)+'\n'+DELETE,
                     text=True,capture_output=True,encoding='utf-8',timeout=300)
    print(r.stderr,end='');r.check_returncode()
    data=json.loads(r.stdout)
    if args.apply:
        output=BASE.parent/f'reports/obsolete-image-deletion-20261112-{args.host}.json'
        with output.open('x',encoding='utf-8') as f:json.dump(data,f,indent=2)
    print(json.dumps({k:data[k] for k in ['root','targets','deleted','free_before','free_after']},indent=2))


if __name__=='__main__':main()
