"""Original services, independently built GPU composer, unchanged bounded return."""
from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-native-original-graphics-boot-035.py'))
inner=p['inner'];outer=p['outer'].replace('native-interactive-035-%s','native-interactive-041-%s').replace('NATIVE_UNATTENDED035','NATIVE_UNATTENDED041')
payload=p['payload'].replace('native-original-graphics-boot-035','native-original-graphics-boot-041').replace("root/'native-render-035'","root/'native-render-041'").replace("local/'render-035.json'","local/'render-041.json'")
assert payload.count('outer='+repr(p['outer']))==1
payload=payload.replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
assert payload.count('gpu_rotation=False')==1
payload=payload.replace('gpu_rotation=False','gpu_rotation_candidate=True,gpu_rotation_runtime_verified=False',1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
