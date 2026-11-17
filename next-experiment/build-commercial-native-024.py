"""Change only our EGL provider's ELF self-binding, retaining original frontend."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-commercial-native-023.py'))
inner=p['inner']
outer=p['outer'].replace('commercial61-native-023-%s','commercial61-native-024-%s').replace('COMMERCIAL023','COMMERCIAL024')
payload=p['payload'].replace('outer='+repr(p['outer']),'outer='+repr(outer),1).replace('commercial61-native-023','commercial61-native-024')
extra=r'''
binding=json.loads((root/'commercial-egl-024/result.json').read_text())
assert not binding['sdk_runtime_libraries_used'] and binding['public_exports_unchanged']
assert binding['new_self_call_locally_bound']
key='native-target/graphics016/system/lib64/libEGL_impl.so'
mode,old_egl=entries[key]
assert hashlib.sha256(old_egl).hexdigest()==binding['original_bridge_sha256']
new_egl=(root/'commercial-egl-024/libEGL_impl.so').read_bytes()
assert hashlib.sha256(new_egl).hexdigest()==binding['bridge_sha256']
entries[key]=(mode,new_egl)
(local/'egl-binding-provenance.json').open('x').write(json.dumps(binding,indent=2))
'''
anchor='def member(name,mode,data,ino):'
assert payload.count(anchor)==1
payload=payload.replace(anchor,extra+'\n'+anchor,1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
