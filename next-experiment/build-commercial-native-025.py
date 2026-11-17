"""Add bounded diagnostics to our provider; original commercial stack unchanged."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-commercial-native-024.py'))
inner=p['inner']
outer=p['outer'].replace('commercial61-native-024-%s','commercial61-native-025-%s').replace('COMMERCIAL024','COMMERCIAL025')
payload=p['payload'].replace('outer='+repr(p['outer']),'outer='+repr(outer),1).replace('commercial61-native-024','commercial61-native-025')
extra=r'''
diagnostic=json.loads((root/'commercial-egl-025/result.json').read_text())
assert diagnostic['diagnostic_only'] and diagnostic['public_exports_unchanged']
assert not diagnostic['sdk_runtime_libraries_used']
assert hashlib.sha256(entries[key][1]).hexdigest()==diagnostic['previous_bridge_sha256']
trace_egl=(root/'commercial-egl-025/libEGL_impl.so').read_bytes()
assert hashlib.sha256(trace_egl).hexdigest()==diagnostic['bridge_sha256']
entries[key]=(entries[key][0],trace_egl)
(local/'egl-trace-provenance.json').open('x').write(json.dumps(diagnostic,indent=2))
'''
anchor='def member(name,mode,data,ino):'
assert payload.count(anchor)==1
payload=payload.replace(anchor,extra+'\n'+anchor,1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
