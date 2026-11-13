"""Recover only an exclusive clone of disposable guest data; preserve source bytes."""
import runpy
from pathlib import Path
import subprocess

parent = runpy.run_path(str(Path(__file__).with_name('audit-original-graphics-crashes-064.py')))['payload']
payload = parent[:parent.index("listing=subprocess.run(")]
payload = payload.replace('baremetal-sdk-original-init-qemu-064', 'baremetal-sdk-original-init-qemu-087')
payload = payload.replace('original-graphics-crashes-064', 'original-audit-copy-087')
payload += r'''
stat_command=['debugfs','-R','stat /graphics-audit-087.log',str(recovered)]
metadata=subprocess.run(stat_command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=20)
(out/'log-stat.stdout').write_bytes(metadata.stdout)
(out/'log-stat.stderr').write_bytes(metadata.stderr)
present=b'Type: regular' in metadata.stdout and b'Inode:' in metadata.stdout
log=dict(present=present,scope='recovered disposable guest data clone')
if present:
 size_match=re.search(rb'\bSize:\s+(\d+)',metadata.stdout)
 assert size_match and int(size_match.group(1))<=64*1024*1024
 dump=subprocess.run(['debugfs','-R','cat /graphics-audit-087.log',str(recovered)],
  stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=40)
 (out/'audit.stderr').write_bytes(dump.stderr)
 assert dump.returncode==0 and len(dump.stdout)==int(size_match.group(1))
 assert not any(word in dump.stderr.lower() for word in (b'checksum',b'not found',b'not open',b'bad magic'))
 with (out/'audit.log').open('xb') as stream:stream.write(dump.stdout)
 log.update(bytes=len(dump.stdout),sha256=hashlib.sha256(dump.stdout).hexdigest())
assert sha(original)==expected
result=dict(recovery=recovery,log=log,original_scratch_unchanged=True,
 original_sdk_images_accessed=False,vm_rerun=False,desktop_verified=False)
(out/'result.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
'''
compile(payload, 'recover-audit-copy-087', 'exec')
if __name__ == '__main__':
    raise SystemExit(subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                                   input=payload, text=True, timeout=180).returncode)
