"""Native Linux decode of exact original assets; not HarmonyOS UI proof."""
from pathlib import Path
import base64
import hashlib
import json
import runpy
import subprocess

b=Path(__file__).resolve().parent
out=b.parent/'reports/commercial-video-decode-test-072'
out.mkdir()
h=runpy.run_path(str(b/'commercial-original-resources-070.py'))
files=h['rawfiles']((b.parent/'reports/commercial-ui-resources-audit-068/HwStartupGuide.hap').read_bytes())
videos={Path(n).name:base64.b64encode(d).decode() for n,d in files.items() if n.endswith('.mp4')}
assert len(videos)==8
w=runpy.run_path(str(b/'commercial-workflow-071.py'))
w['configure_local_transport']()
code=r'''
from pathlib import Path
import base64,hashlib,json,os,subprocess,time
root=Path.home()/'.local/share/harmony-arm64-kvm-lab/codec-software-test-072'
root.mkdir(mode=0o700)
boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
timer=['systemctl','is-active','harmony-lab-screen-off-001.timer']
assert subprocess.check_output(timer,text=True).strip()=='active'
version=subprocess.check_output(['ffmpeg','-version'],text=True)
assert 'ffmpeg version 8.0.1' in version.splitlines()[0]
rows=[]
for name,encoded in sorted(VIDEOS.items()):
 assert name.endswith('.mp4') and Path(name).name==name
 source=root/name;data=base64.b64decode(encoded,validate=True)
 with source.open('xb') as out:out.write(data)
 source.chmod(0o444)
 probe=subprocess.run(['ffprobe','-v','error','-select_streams','v:0',
  '-show_entries','stream=codec_name,width,height,pix_fmt,nb_frames,duration','-of','json',str(source)],
  capture_output=True,text=True,timeout=30)
 assert probe.returncode==0,probe.stderr
 info=json.loads(probe.stdout)
 target=root/(name+'.framemd5')
 started=time.monotonic()
 run=subprocess.run(['ffmpeg','-nostdin','-v','error','-threads','2','-i',str(source),
  '-map','0:v:0','-an','-f','framemd5',str(target)],capture_output=True,text=True,timeout=120)
 elapsed=time.monotonic()-started
 (root/(name+'.stderr')).open('x').write(run.stderr)
 body=target.read_bytes() if target.exists() else b''
 frames=[line for line in body.decode().splitlines() if line and not line.startswith('#')]
 unchanged=hashlib.sha256(source.read_bytes()).hexdigest()==hashlib.sha256(data).hexdigest()
 rows.append(dict(name=name,source_bytes=len(data),source_sha256=hashlib.sha256(data).hexdigest(),
  original_source_unchanged=unchanged,probe=info,decode_return=run.returncode,
  decode_seconds=elapsed,frames=len(frames),framemd5_sha256=hashlib.sha256(body).hexdigest(),
  decode_stderr=run.stderr,actual_native_software_decode=run.returncode==0 and len(frames)>0))
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()==boot
assert subprocess.check_output(timer,text=True).strip()=='active'
result=dict(boot_id=boot,workdir=str(root),ffmpeg_version=version.splitlines()[0],videos=rows,
 all_original_sources_unchanged=all(r['original_source_unchanged'] for r in rows),
 all_eight_decoded=all(r['actual_native_software_decode'] for r in rows),
 packages_installed=False,system_configuration_changed=False,host_rebooted=False,
 harmonyos_backend_integrated=False,desktop_verified=False,interaction_verified=False)
with (root/'result.json').open('x') as out:json.dump(result,out,indent=2)
print(json.dumps(result,indent=2))
'''
code='VIDEOS='+repr(videos)+'\n'+code
command=['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',
 '-o','HostName=192.168.10.128','-o','HostKeyAlias=192.168.10.128',
 '-o','ConnectTimeout=10','matebook','python3 -']
result=subprocess.run(command,input=code,text=True,capture_output=True,timeout=1100)
(out/'ssh.stdout').open('x').write(result.stdout)
(out/'ssh.stderr').open('x').write(result.stderr)
assert result.returncode==0,result.stderr
decoded=json.loads(result.stdout)
for item in decoded['videos']:
    original=files['resources/rawfile/'+item['name']]
    assert item['source_sha256']==hashlib.sha256(original).hexdigest()
(out/'result.json').open('x').write(json.dumps(decoded,indent=2))
print(json.dumps(decoded,indent=2))
