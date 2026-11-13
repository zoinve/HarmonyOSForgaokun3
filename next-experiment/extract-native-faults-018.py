"""Reconstruct only complete, unchanged original fault files from hashed snapshots."""
from pathlib import Path
import hashlib,json,re

def extract(text):
    rows=[]; current=None
    for line in text.splitlines():
        m=re.fullmatch(r'NATIVE_FAULT018_BEGIN sample=(\d+) path=(\S+) size=(\d+) fd=(\d+) errno=0',line)
        if m:
            current=dict(sample=int(m[1]),path=m[2],size=int(m[3]),data=bytearray());continue
        m=re.fullmatch(r'NATIVE_FAULT018_HEX sample=(\d+) path=(\S+) offset=(\d+) data=([0-9a-f]+)',line)
        if m and current:
            assert (int(m[1]),m[2],int(m[3]))==(current['sample'],current['path'],len(current['data']))
            current['data'].extend(bytes.fromhex(m[4]));continue
        m=re.fullmatch(r'NATIVE_FAULT018_END sample=(\d+) path=(\S+) bytes=(\d+) complete=1 changed=0 read_errno=0',line)
        if m and current:
            assert (int(m[1]),m[2],int(m[3]))==(current['sample'],current['path'],current['size'])
            assert len(current['data'])==current['size']
            current['data']=bytes(current['data']);rows.append(current);current=None
    return rows

if __name__=='__main__':
    root=Path(__file__).resolve().parent.parent/'reports/native-original-graphics-boot-018'
    runtime=json.loads((root/'runtime-result.json').read_text())
    for row in runtime['logs']:
        assert hashlib.sha256((root/'native-logs'/row['name']).read_bytes()).hexdigest()==row['sha256']
    rows=extract((root/'native-logs/phase-049.log').read_bytes().decode(errors='replace'))
    assert rows
    output=root/'fault-files';output.mkdir()
    manifest=[]
    for row in rows:
        name=Path(row['path']).name
        with (output/name).open('xb') as f:f.write(row['data'])
        manifest.append(dict(sample=row['sample'],original_path=row['path'],name=name,bytes=len(row['data']),sha256=hashlib.sha256(row['data']).hexdigest()))
    with (root/'fault-extraction.json').open('x') as f:json.dump(manifest,f,indent=2)
    print(json.dumps(manifest,indent=2))
