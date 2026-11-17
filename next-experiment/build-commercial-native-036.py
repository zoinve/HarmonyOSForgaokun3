"""Use pinned HarmonyMac readiness and L410 namespace implementation."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-commercial-native-035.py'))
inner=p['inner']
anchor='    commercial_copy005("/graphics016/system/bin/l410_launch_appspawn_r18_namespace.sh","/run/commercial-system005/upper/bin/l410_launch_appspawn_r18_namespace.sh",0755);'
assert inner.count(anchor)==1
extra='\n    directory("/run/commercial-system005/upper/bin/aurora",0755);\n'
for name in ['samgr-service-probe','appspawn-reference-namespace']:
    extra+=f'    commercial_copy005("/graphics016/system/bin/aurora/{name}","/run/commercial-system005/upper/bin/aurora/{name}",0755);\n'
inner=inner.replace(anchor,anchor+extra,1)
outer=p['outer'].replace('commercial61-native-035-%s','commercial61-native-036-%s').replace('COMMERCIAL035','COMMERCIAL036')
payload=p['payload'].replace('inner='+repr(p['inner']),'inner='+repr(inner),1).replace('outer='+repr(p['outer']),'outer='+repr(outer),1).replace('commercial61-native-035','commercial61-native-036')
payload=payload.replace("base/'commercial-desktop-retry-032.py'","base/'commercial-reference-start-036.py'")
anchor="launcher=runpy.run_path(str(base/'commercial-appspawn-018.py'))['repair'](original)"
assert payload.count(anchor)==1
payload=payload.replace(anchor,anchor+"\nlauncher=runpy.run_path(str(base/'commercial-reference-namespace-036.py'))['launcher'](launcher)",1)
anchor="entries=runpy.run_path(str(base/'commercial-archive-017.py'))['complete'](entries)"
assert payload.count(anchor)==1
extra=r'''
for folder,binary,field in [
 ('commercial-reference-probe-036-r3','samgr-service-probe','probe_sha256'),
 ('commercial-reference-namespace-036','appspawn-reference-namespace','binary_sha256')]:
 evidence=json.loads((root/folder/'result.json').read_text())
 data=(root/folder/binary).read_bytes()
 assert hashlib.sha256(data).hexdigest()==evidence[field]
 key='native-target/graphics016/system/bin/aurora/'+binary
 assert key not in entries
 entries[key]=(stat.S_IFREG|0o755,data)
 (local/(binary+'-provenance.json')).open('x').write(json.dumps(evidence,indent=2))
reference_start=runpy.run_path(str(base/'commercial-reference-start-036.py'))
(local/'reference-start-provenance.json').open('x').write(json.dumps(reference_start['provenance'](),indent=2))
'''
payload=payload.replace(anchor,extra+'\n'+anchor,1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
