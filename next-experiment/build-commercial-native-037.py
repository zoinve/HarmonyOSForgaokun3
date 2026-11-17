"""Correct commercial startup order observed in 036; retain L410 namespace."""
from pathlib import Path
import runpy,subprocess
p=runpy.run_path(str(Path(__file__).with_name('build-commercial-native-036.py')))
inner=p['inner']
outer=p['outer'].replace('commercial61-native-036','commercial61-native-037').replace('COMMERCIAL036','COMMERCIAL037')
payload=p['payload'].replace('outer='+repr(p['outer']),'outer='+repr(outer),1).replace('commercial61-native-036','commercial61-native-037')
old="patched=runpy.run_path(str(base/'commercial-reference-start-036.py'))['repair'](patched)"
new="patched=runpy.run_path(str(base/'commercial-desktop-retry-032.py'))['repair'](patched)"
assert payload.count(old)==1
payload=payload.replace(old,new,1)
# 036 reference readiness provenance remains source provenance, not a claim that its gate is used.
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=600).returncode)
