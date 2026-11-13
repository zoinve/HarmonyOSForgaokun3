"""Manual native-cursor candidate: retain 031 Binder kernel and genuine MMI input."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-native-original-graphics-boot-031.py'))
inner=p['inner']
anchor='"libEGL_impl.so", "lab-freedreno003/libEGL.so.1",'
assert inner.count(anchor)==1
inner=inner.replace(anchor,'"libcursor_drawing_adapter.z.so", "libcursor_drawing_adapter032.z.so",\n        '+anchor,1)
anchor='    pid_t observer = fork();'
assert inner.count(anchor)==1
inner=inner.replace(anchor,r'''
    int cursor032=open("/data/native-cursor032.state",O_RDWR|O_CREAT|O_EXCL|O_CLOEXEC|O_NOFOLLOW,0640);
    if(cursor032<0 || ftruncate(cursor032,64) || fchown(cursor032,6696,1003) ||
        fchmod(cursor032,0640) || close(cursor032))fail("native cursor state");
    dprintf(1,"NATIVE_CURSOR032 state_owner=6696 state_group=1003 mode=0640 input_injection=0\n");
'''+anchor,1)
outer=p['outer'].replace('native-interactive-031-%s','native-interactive-032-%s').replace('NATIVE_INTERACTIVE031','NATIVE_INTERACTIVE032')
payload=p['payload'].replace('native-original-graphics-boot-031','native-original-graphics-boot-032')
assert payload.count('inner='+repr(p['inner']))==1
payload=payload.replace('inner='+repr(p['inner']),'inner='+repr(inner),1)
payload=payload.replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
addition=r'''
cursor_work=root/'native-cursor-032-r2'
cursor_result=json.loads((cursor_work/'result.json').read_text())
for n,h in cursor_result['sha256'].items():assert sha(cursor_work/n)==h,n
target='native-target/graphics-provider/libdisplay_composer_vdi_impl.z.so'
assert target in entries
entries[target]=(entries[target][0],(cursor_work/'libdisplay_composer_vdi_impl.z.so').read_bytes())
for n in ['libcursor_drawing_adapter.z.so','libcursor_drawing_adapter032.z.so']:
 file('native-target/graphics-egl/'+n,cursor_work/n)
with (local/'cursor-bridge-032.json').open('x') as f:
 json.dump(dict(cursor=cursor_result,kernel_031_retained=True,input_injection=False,statusbar_resolution_changed=False,runtime_verified=False),f,indent=2)
'''
anchor='def member(name,mode,data,ino):'
assert payload.count(anchor)==1
payload=payload.replace(anchor,addition+'\n'+anchor,1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
