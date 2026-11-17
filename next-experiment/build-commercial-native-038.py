"""Observe actual scanout after SceneBoard first flush, retaining all drawing behavior."""
from pathlib import Path
import runpy,subprocess
p=runpy.run_path(str(Path(__file__).with_name('build-commercial-native-037.py')))
inner=p['inner']
old='if(sample!=3 && sample!=9 && sample!=15)return;'
assert inner.count(old)==1
inner=inner.replace(old,'if(sample!=3 && sample!=9 && sample!=15 && sample!=16 && sample!=17)return;',1)
outer=p['outer'].replace('commercial61-native-037','commercial61-native-038').replace('COMMERCIAL037','COMMERCIAL038')
old='if(elapsed033%15==0)snapshot();'
assert outer.count(old)==1
outer=outer.replace(old,'if(elapsed033%15==0 || elapsed033==85 || elapsed033==89)snapshot();',1)
payload=p['payload'].replace('inner='+repr(p['inner']),'inner='+repr(inner),1).replace('outer='+repr(p['outer']),'outer='+repr(outer),1).replace('commercial61-native-037','commercial61-native-038')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
