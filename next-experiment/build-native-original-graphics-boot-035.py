from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent
p=runpy.run_path(str(base/'build-native-original-graphics-boot-034.py'))
inner=p['inner'];outer=p['outer'].replace('native-interactive-034-%s','native-interactive-035-%s').replace('NATIVE_UNATTENDED034','NATIVE_UNATTENDED035')
payload=p['payload'].replace('native-original-graphics-boot-034','native-original-graphics-boot-035').replace("root/'native-render-034'","root/'native-render-035'").replace("local/'render-034.json'","local/'render-035.json'")
assert payload.count('outer='+repr(p['outer']))==1
payload=payload.replace('outer='+repr(p['outer']),'outer='+repr(outer),1)
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
