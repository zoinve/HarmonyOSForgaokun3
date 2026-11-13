"""Original graph unchanged; add a separately identified read-only API diagnostic."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('run-baremetal-sdk-original-init-082.py')))['payload']
for old, new in [('original-init-qemu-082','original-init-qemu-083'),
                 ('harmony-sdk-qemu082-','harmony-sdk-qemu083-'),
                 ('original-init-082/result.json','original-init-083/result.json'),
                 ('GRAPHICS082_','GRAPHICS083_'),('ORIGINAL_INIT082_','ORIGINAL_INIT083_')]:
    assert old in payload, old
    payload = payload.replace(old,new)
anchor = "add('graphics-init.cfg',stat.S_IFREG|0o444,Path(prep['files']['graphics-init.cfg']['path']).read_bytes())"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, '''query=json.loads((root/'original-config-query-001/result.json').read_text())
query_bytes=Path(query['path']).read_bytes()
assert len(query_bytes)==query['bytes'] and hashlib.sha256(query_bytes).hexdigest()==query['sha256']
add('graphics-config-query',stat.S_IFREG|0o755,query_bytes)
''' + anchor)
compile(payload, 'original-config-query-083-run', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=660).returncode)
