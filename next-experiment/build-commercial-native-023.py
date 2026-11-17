"""Restore original mapper visibility with only four MateBook GPU overrides."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-commercial-native-022.py'))
inner=p['inner']
start=inner.index('static void commercial_vendor016(void)\n{')
end=inner.index('\n}\n',start)
extra='    directory("/run/commercial-vendor004/upper/lib64/passthrough",0755);\n'
for name in ['libEGL_impl.so','libGLESv1_impl.so','libGLESv2_impl.so','libGLESv3_impl.so']:
    extra+=f'    commercial_copy005("/graphics016/system/lib64/{name}","/run/commercial-vendor004/upper/lib64/passthrough/{name}",0644);\n'
inner=inner[:end]+'\n'+extra+inner[end:]
outer=p['outer'].replace('commercial61-native-022-%s','commercial61-native-023-%s').replace('COMMERCIAL022','COMMERCIAL023')
payload=p['payload'].replace('inner='+repr(p['inner']),'inner='+repr(inner),1).replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
payload=payload.replace('commercial61-native-022','commercial61-native-023')
anchor="alias=runpy.run_path(str(base/'commercial-sceneboard-mounts-022.py'))['repair'](alias)"
assert payload.count(anchor)==1
payload=payload.replace(anchor,anchor+"\nalias=runpy.run_path(str(base/'commercial-mapper-path-023.py'))['repair'](alias)",1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
