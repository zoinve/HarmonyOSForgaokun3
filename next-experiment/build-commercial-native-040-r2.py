"""Use reference symlinks so all loader paths share the same EGL/Mesa instance."""
from pathlib import Path
import runpy,subprocess
p=runpy.run_path(str(Path(__file__).with_name('build-commercial-native-040.py')))
inner=p['inner']
for source,name,target in [('libEGL_impl.so','libEGL.so','libEGL_impl.so'),('libGLESv3_impl.so','libGLESv3.so','/system/lib64/lab-commercial013/libGLESv2.so.2'),('libGLESv2_impl.so','libGLESv2.so','/system/lib64/lab-commercial013/libGLESv2.so.2')]:
 old=f'    commercial_copy005("/graphics016/system/lib64/{source}","/run/commercial-system005/upper/lib64/{name}",0644);'
 assert inner.count(old)==1
 new=f'    if(symlink("{target}","/run/commercial-system005/upper/lib64/{name}"))fail("reference direct {name} symlink");'
 inner=inner.replace(old,new,1)
outer=p['outer']
payload=p['payload'].replace('inner='+repr(p['inner']),'inner='+repr(inner),1)
payload=payload.replace("work=root/'commercial61-native-040';local=base.parent/'reports/commercial61-native-040'","work=root/'commercial61-native-040-r2';local=base.parent/'reports/commercial61-native-040-r2'",1)
assert "work=root/'commercial61-native-040-r2'" in payload
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
