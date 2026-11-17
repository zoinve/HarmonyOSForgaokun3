"""Follow HarmonyMac's real direct EGL/GLES board-backend route in a volatile overlay."""
from pathlib import Path
import runpy,subprocess
b=Path(__file__).resolve().parent
p=runpy.run_path(str(b/'build-commercial-native-039.py'))
inner=p['inner']
anchor='    commercial_copy005("/graphics016/system/lib64/libEGL_impl.so","/run/commercial-system005/upper/lib64/libEGL_impl.so",420);'
assert inner.count(anchor)==1
extra='''
    /* HarmonyMac prepare-render-service-test.sh: direct board EGL/Mesa frontend.
       Only volatile RAM overlay files; original commercial images stay intact. */
    commercial_copy005("/graphics016/system/lib64/libEGL_impl.so","/run/commercial-system005/upper/lib64/libEGL.so",0644);
    commercial_copy005("/graphics016/system/lib64/libGLESv3_impl.so","/run/commercial-system005/upper/lib64/libGLESv3.so",0644);
    commercial_copy005("/graphics016/system/lib64/libGLESv2_impl.so","/run/commercial-system005/upper/lib64/libGLESv2.so",0644);
'''
inner=inner.replace(anchor,anchor+extra,1)
outer=p['outer'].replace('commercial61-native-039','commercial61-native-040').replace('COMMERCIAL039','COMMERCIAL040')
payload=p['payload'].replace('inner='+repr(p['inner']),'inner='+repr(inner),1).replace('outer='+repr(p['outer']),'outer='+repr(outer),1).replace('commercial61-native-039','commercial61-native-040')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
