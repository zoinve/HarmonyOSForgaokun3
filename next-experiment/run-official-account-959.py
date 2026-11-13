"""Fresh account CLI trial; no authentication files or policies are patched."""
from pathlib import Path
import hashlib
import json
import subprocess

base=Path(__file__).resolve().parent
parent=base/'official-arm-run-958';out=base/'official-arm-run-959'
remote='/home/zoinve/.local/share/harmony-arm64-kvm-lab/official-arm-sdk-921/full-system-959'
assert not out.exists()
assert (base.parent/'reports/userdata-cleanup-official-958.json').is_file()
payload=base/'official-account-init-959/initramfs.cpio.gz'
manifest=json.loads((payload.parent/'manifest.json').read_text())
assert hashlib.sha256(payload.read_bytes()).hexdigest()==manifest['sha256']
c=json.loads((parent/'config.json').read_text())
c['command']=[a.replace('full-system-958/','full-system-959/') for a in c['command']]
vendor=c['disks'][1]['path']
c['command']=[a.replace(vendor.replace('full-system-958/','full-system-959/'),vendor) for a in c['command']]
c['disks'][3]['path']=remote+'/userdata-permissive.img'
for row in c['inputs']:
    if 'full-system-958/' in row['remote']:
        row['remote']=row['remote'].replace('full-system-958/','full-system-959/')
        assert row['remote'].endswith('/initramfs.cpio.gz')
        row['sha256']=manifest['sha256']
        if 'bytes' in row:row['bytes']=payload.stat().st_size
        if 'size' in row:row['size']=payload.stat().st_size
append=c['command'].index('-append')+1
assert 'rdinit=/init' in c['command'][append]
c['command'][append]=c['command'][append].replace('rdinit=/init','rdinit=/lab-account-init')
c['authorized_account_creation']='normal local user labuser via unmodified acm; retain original user'
source=(parent/'runner.py').read_text().replace('full-system-958','full-system-959')
source=source.replace('identities_modified=False','identities_modified=False,normal_local_account_creation_authorized=True')
compile(source,'runner-959','exec')
assert sum('readonly=on' in a for a in c['command'])==3
subprocess.run(['ssh','matebook','mkdir '+remote],check=True)
out.mkdir();(out/'config.json').write_text(json.dumps(c,indent=2));(out/'runner.py').write_text(source)
for path,name in [(payload,'initramfs.cpio.gz'),(out/'config.json','config.json'),(out/'runner.py','runner.py')]:
    subprocess.run(['scp',str(path),'matebook:'+remote+'/'+name],check=True)
with (out/'host.stdout').open('xb') as stdout,(out/'host.stderr').open('xb') as stderr:
    process=subprocess.run(['ssh','matebook','sudo -n python3 '+remote+'/runner.py'],stdout=stdout,stderr=stderr,timeout=900)
for name in ('result.json','serial.log','stderr.log','config.json','userdata-capacity-check.txt'):
    subprocess.run(['scp','matebook:'+remote+'/'+name,str(out/name)],check=True)
d=json.loads((out/'result.json').read_text())
for shot in d['screenshots']:
    subprocess.run(['scp','matebook:'+remote+'/'+shot['name'],str(out/shot['name'])],check=True)
flags=('readonly_inputs_unchanged','official_originals_unchanged','protected_userdata_original_unchanged')
print(json.dumps({k:d.get(k) for k in ('returncode','elapsed_seconds')+flags},indent=2))
assert process.returncode==0 and all(d[k] for k in flags)
