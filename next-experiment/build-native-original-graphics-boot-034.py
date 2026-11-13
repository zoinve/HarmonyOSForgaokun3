"""One bounded real-service run of the NEON/copy-reduction composer."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-native-original-graphics-boot-033.py'))
inner=p['inner']
outer=p['outer'].replace('native-interactive-033-%s','native-interactive-034-%s').replace('NATIVE_UNATTENDED033','NATIVE_UNATTENDED034')
payload=p['payload'].replace('native-original-graphics-boot-033','native-original-graphics-boot-034')
assert payload.count('outer='+repr(p['outer']))==1
payload=payload.replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
addition=r'''
render_work=root/'native-render-034'
render_result=json.loads((render_work/'result.json').read_text())
for n,h in render_result['sha256'].items():assert sha(render_work/n)==h,n
assert render_result['sha256']['libcursor_drawing_adapter.z.so']==cursor_result['sha256']['libcursor_drawing_adapter.z.so']
target='native-target/graphics-provider/libdisplay_composer_vdi_impl.z.so'
entries[target]=(entries[target][0],(render_work/'libdisplay_composer_vdi_impl.z.so').read_bytes())
with (local/'render-034.json').open('x') as f:
 json.dump(dict(render=render_result,cursor_unchanged=True,auto_return_seconds=420,target_budget_seconds=240,
  gpu_rotation=False,desktop_fps_verified=False,runtime_verified=False),f,indent=2)
'''
anchor='def member(name,mode,data,ino):'
assert payload.count(anchor)==1
payload=payload.replace(anchor,addition+'\n'+anchor,1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
