"""Observe the real post-flush render interval with a separate bounded Ubuntu return."""
from pathlib import Path
import runpy,subprocess
b=Path(__file__).resolve().parent
p=runpy.run_path(str(b/'build-commercial-native-038.py'))
inner=runpy.run_path(str(b/'commercial-task-observer-039.py'))['instrument'](p['inner'])
old='if(sample!=3 && sample!=9 && sample!=15 && sample!=16 && sample!=17)return;'
assert inner.count(old)==1
inner=inner.replace(old,'if(sample!=3 && sample!=9 && sample!=15 && sample!=17 && sample!=20 && sample!=24 && sample!=28)return;',1)
outer=p['outer'].replace('commercial61-native-038','commercial61-native-039').replace('COMMERCIAL038','COMMERCIAL039')
for old,new in [('target_budget_seconds=90','target_budget_seconds=150'),('elapsed033<90','elapsed033<150'),('left033=210','left033=270')]:
 assert outer.count(old)==1,(old,outer.count(old))
 outer=outer.replace(old,new,1)
payload=p['payload'].replace('inner='+repr(p['inner']),'inner='+repr(inner),1).replace('outer='+repr(p['outer']),'outer='+repr(outer),1).replace('commercial61-native-038','commercial61-native-039')
assert 'outer_deadline_seconds=210' in payload and 'target_budget_seconds=90' in payload
payload=payload.replace('outer_deadline_seconds=210','outer_deadline_seconds=270').replace('target_budget_seconds=90','target_budget_seconds=150')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
