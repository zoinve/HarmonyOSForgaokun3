"""Observe original application public transaction path under the actual reference route."""
from pathlib import Path
import runpy,subprocess
b=Path(__file__).resolve().parent
p=runpy.run_path(str(b/'build-commercial-native-040-r2.py'))
inner=p['inner']
anchor='    commercial_copy005("/graphics016/system/lib64/libEGL_impl.so","/run/commercial-system005/upper/lib64/libEGL_impl.so",420);'
assert inner.count(anchor)==1
inner=inner.replace(anchor,anchor+'\n    commercial_copy005("/graphics016/system/lib64/libcommercial_rs_observer041.so","/run/commercial-system005/upper/lib64/libcommercial_rs_observer041.so",0644);',1)
outer=p['outer'].replace('commercial61-native-040','commercial61-native-041').replace('COMMERCIAL040','COMMERCIAL041')
payload=p['payload'].replace('inner='+repr(p['inner']),'inner='+repr(inner),1).replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
payload=payload.replace('commercial61-native-040-r2','commercial61-native-041').replace('commercial61-native-040','commercial61-native-041')
extra=r'''
observer=root/'commercial-rs-observer-041'
observation=json.loads((observer/'result.json').read_text())
namespace_observation=json.loads((observer/'namespace-result.json').read_text())
for filename,field,evidence,key in [
 ('libcommercial_rs_observer041.so','library_sha256',observation,'native-target/graphics016/system/lib64/libcommercial_rs_observer041.so'),
 ('appspawn-reference-namespace','binary_sha256',namespace_observation,'native-target/graphics016/system/bin/aurora/appspawn-reference-namespace')]:
 data=(observer/filename).read_bytes();assert hashlib.sha256(data).hexdigest()==evidence[field]
 mode=entries[key][0] if key in entries else stat.S_IFREG|0o644
 entries[key]=(mode,data)
 (local/(filename+'-observation-provenance.json')).open('x').write(json.dumps(evidence,indent=2))
'''
anchor='def member(name,mode,data,ino):'
assert payload.count(anchor)==1
payload=payload.replace(anchor,extra+'\n'+anchor,1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
