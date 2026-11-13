"""Extract and inspect original client/service contracts without executing them."""
from pathlib import Path
import hashlib
import json
import subprocess

BASE = Path(__file__).resolve().parent.parent
OUT = BASE / 'reports/composer-smq-001'
PAYLOAD = r'''
from pathlib import Path
import hashlib,json,subprocess
root=Path('/home/zoinve/harmony-virgl-883')
dest=root/'composer-smq-audit-001'
assert not dest.exists(),dest
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
image=Path('/mnt/d/Download/pc_all_arm/system.img')
before=digest(image)
dest.mkdir()
results={};inputs=[]
names=['libdisplay_composer_hdi_impl_1.5.z.so','libdisplay_composer_proxy_1.5.z.so']
for name in names:
 target=dest/name
 command=['debugfs','-R','dump /system/lib64/'+name+' '+str(target),str(image)]
 p=subprocess.run(command,text=True,capture_output=True,timeout=30)
 assert p.returncode==0 and target.is_file(),(command,p.stderr)
 body=target.read_bytes()
 assert body[:6]==b'\x7fELF\x02\x01' and int.from_bytes(body[18:20],'little')==183
 inputs.append(dict(path=str(target),image_path='/system/lib64/'+name,sha256=digest(target),bytes=len(body)))
service=root/'composer-service-957-build2/libdisplay_composer_service_1.5.z.so'
assert digest(service)=='c5f7b2430aac4bee8edbeaea707805c0d9f33f6ee762a4a1f82452be01f92aab'
inputs.append(dict(path=str(service),sha256=digest(service),bytes=service.stat().st_size))
for item in inputs:
 path=item['path'];short=Path(path).name
 for label,tool in [('symbols',['aarch64-linux-gnu-nm','-DC']),('disassembly',['aarch64-linux-gnu-objdump','-dC']),('dynamic',['aarch64-linux-gnu-readelf','-dW'])]:
  command=tool+[path]
  p=subprocess.run(command,text=True,capture_output=True,timeout=30)
  assert p.returncode==0,(command,p.stderr)
  results[short+'.'+label]=dict(command=command,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr)
after=digest(image)
assert before==after,'source image changed'
print(json.dumps(dict(image=dict(path=str(image),sha256_before=before,sha256_after=after,bytes=image.stat().st_size),inputs=inputs,results=results)))
'''


def main():
    assert not OUT.exists(), OUT
    p = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'],
                       input=PAYLOAD, text=True, capture_output=True, timeout=300)
    assert p.returncode == 0, p.stderr
    data = json.loads(p.stdout)
    OUT.mkdir()
    artifacts = []
    for name, row in data.pop('results').items():
        for stream in ('stdout', 'stderr'):
            body = row[stream].encode()
            path = OUT / (name + '.' + stream)
            with path.open('xb') as f:
                f.write(body)
            artifacts.append(dict(path=path.name, bytes=len(body),
                                  sha256=hashlib.sha256(body).hexdigest()))
    data.update(artifacts=artifacts, source_image_unchanged=True,
                elf_executed=False, device_access=False, matebook_changed=False,
                serialization_verified=False, native_hdi_runtime_verified=False)
    with (OUT / 'result.json').open('x', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(json.dumps(data, indent=2))


if __name__ == '__main__':
    main()
