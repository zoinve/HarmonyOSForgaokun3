"""Fresh 30-minute display run in the logged-in Ubuntu user session."""
from pathlib import Path
import json
import subprocess

base=Path(__file__).resolve().parent
parent=base/'official-arm-run-958';out=base/'official-arm-run-961'
remote='/home/zoinve/.local/share/harmony-arm64-kvm-lab/official-arm-sdk-921/full-system-961'
assert not out.exists()
assert (base.parent/'reports/userdata-cleanup-official-960.json').is_file()
c=json.loads((parent/'config.json').read_text())
vendor=c['disks'][1]['path']
c['command']=[a.replace('full-system-958/','full-system-961/') for a in c['command']]
c['command']=[a.replace(remote+'/vendor-graphics.img',vendor) for a in c['command']]
for row in c['inputs']:row['remote']=row['remote'].replace('full-system-958/','full-system-961/')
c['disks'][3]['path']=remote+'/userdata-permissive.img'
assert c['disks'][1]['path']==vendor and sum('readonly=on' in a for a in c['command'])==3
assert 'rdinit=/init' in c['command'][c['command'].index('-append')+1]
source=(parent/'runner.py').read_text().replace('full-system-958','full-system-961')
source=source.replace('elapsed>=360','elapsed>=1800').replace('wall_limit_seconds=360','wall_limit_seconds=1800').replace('bounded_360s','bounded_1800s')
source=source.replace('next_shot=next_shot+30','next_shot=next_shot+120')
anchor="qmp({'execute':'cont'});d['guest_started']=True"
assert source.count(anchor)==1
source=source.replace(anchor,anchor+"\n  with (o/'viewer-launch.log').open('xb') as viewer_log:\n   subprocess.run(['/usr/bin/python3',str(o/'physical-viewer-launch.py')],stdout=viewer_log,stderr=viewer_log,timeout=20,check=True)")
compile(source,'runner-961','exec')
# Reuse the working FD-passing viewer, targeting the logged-in user, never GDM.
text=(base/'show-physical-960.py').read_text()
ns={'__file__':str(base/'show-physical-960.py')}
exec(text[:text.index("r=subprocess.run(['ssh'")],ns)
viewer=ns['remote'].replace('full-system-960','full-system-961').replace("pwd.getpwnam('gdm-greeter')","pwd.getpwnam('zoinve')")
compile(viewer,'physical-viewer-launch','exec')
subprocess.run(['ssh','matebook','mkdir '+remote],check=True)
out.mkdir()
(out/'config.json').write_text(json.dumps(c,indent=2));(out/'runner.py').write_text(source)
(out/'physical-viewer-launch.py').write_text(viewer)
for path,name in [(out/'config.json','config.json'),(out/'runner.py','runner.py'),(out/'physical-viewer-launch.py','physical-viewer-launch.py'),(base/'official-arm-mount-921/initramfs.cpio.gz','initramfs.cpio.gz')]:
    subprocess.run(['scp',str(path),'matebook:'+remote+'/'+name],check=True)
with (out/'host.stdout').open('xb') as stdout,(out/'host.stderr').open('xb') as stderr:
    process=subprocess.run(['ssh','matebook','sudo -n python3 '+remote+'/runner.py'],stdout=stdout,stderr=stderr,timeout=2400)
for name in ('result.json','serial.log','stderr.log','config.json','userdata-capacity-check.txt','viewer-launch.log','physical-viewer.log'):
    subprocess.run(['scp','matebook:'+remote+'/'+name,str(out/name)],check=True)
d=json.loads((out/'result.json').read_text())
for shot in d['screenshots']:
    subprocess.run(['scp','matebook:'+remote+'/'+shot['name'],str(out/shot['name'])],check=True)
flags=('readonly_inputs_unchanged','official_originals_unchanged','protected_userdata_original_unchanged')
print(json.dumps({k:d.get(k) for k in ('returncode','elapsed_seconds')+flags},indent=2))
assert process.returncode==0 and all(d[k] for k in flags)
