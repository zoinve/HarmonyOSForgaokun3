"""Fresh full-system integration of independently verified real KMS composer."""
from pathlib import Path
import hashlib
import json
import subprocess

base=Path(__file__).resolve().parent
parent=base/'official-arm-run-951';out=base/'official-arm-run-958'
remote='/home/zoinve/.local/share/harmony-arm64-kvm-lab/official-arm-sdk-921/full-system-958'
assert not out.exists()
assert (base.parent/'reports/userdata-cleanup-official-951.json').is_file()
manifest=json.loads((base/'official-system-958/manifest.json').read_text())
assert manifest['original_images_unchanged'] and not manifest['activation_modified']
c=json.loads((parent/'config.json').read_text())
c['command']=[a.replace('full-system-951/','full-system-958/') for a in c['command']]
for row in c['inputs']:row['remote']=row['remote'].replace('full-system-951/','full-system-958/')
row=c['disks'][1];old=row['path']
row.update(path=remote+'/vendor-graphics.img',bytes=manifest['images'][1]['bytes'],sha256=manifest['images'][1]['sha256'])
c['command']=[a.replace(old,row['path']) for a in c['command']]
c['disks'][3]['path']=remote+'/userdata-permissive.img'
c['command']+=['-vnc','unix:'+remote+'/vnc.sock']
assert c['originals']==json.loads((parent/'config.json').read_text())['originals']
assert sum('readonly=on' in a for a in c['command'])==3
assert ' enforcing=0' in c['command'][c['command'].index('-append')+1]
source=(parent/'runner.py').read_text().replace('full-system-951','full-system-958')
begin=source.index('    try:\n     qmp({\'execute\':\'screendump\'')
end=source.index('    next_shot=next_shot+30',begin)
source=source[:begin]+'''    try:
     frame=capture_rfb(o,target)
     frame['host_elapsed_seconds']=elapsed
     d['screenshots'].append(frame)
    except Exception as exc:
     d.setdefault('screenshot_unavailable',[]).append(dict(host_elapsed_seconds=elapsed,reason=repr(exc)))
'''+source[end:]
source=(base/'rfb-framebuffer.py').read_text()+'\n'+source
compile(source,'runner-958','exec')
vendor=Path('//wsl.localhost/Debian'+manifest['images'][1]['path'])
assert vendor.is_file()
with vendor.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==manifest['images'][1]['sha256']
subprocess.run(['ssh','matebook','mkdir '+remote],check=True)
out.mkdir();(out/'config.json').write_text(json.dumps(c,indent=2));(out/'runner.py').write_text(source)
for path,name in [(vendor,'vendor-graphics.img'),(out/'config.json','config.json'),(out/'runner.py','runner.py'),(base/'official-arm-mount-921/initramfs.cpio.gz','initramfs.cpio.gz')]:
    subprocess.run(['scp',str(path),'matebook:'+remote+'/'+name],check=True)
with (out/'host.stdout').open('xb') as stdout,(out/'host.stderr').open('xb') as stderr:
    process=subprocess.run(['ssh','matebook','sudo -n python3 '+remote+'/runner.py'],stdout=stdout,stderr=stderr,timeout=900)
for name in ('result.json','serial.log','stderr.log','config.json','userdata-capacity-check.txt'):
    subprocess.run(['scp','matebook:'+remote+'/'+name,str(out/name)],check=True)
d=json.loads((out/'result.json').read_text())
for shot in d['screenshots']:
    subprocess.run(['scp','matebook:'+remote+'/'+shot['name'],str(out/shot['name'])],check=True)
flags=('readonly_inputs_unchanged','official_originals_unchanged','protected_userdata_original_unchanged')
print(json.dumps({k:d.get(k) for k in ('returncode','elapsed_seconds','screenshots','screenshot_unavailable')+flags},indent=2))
assert process.returncode==0 and all(d[k] for k in flags)
