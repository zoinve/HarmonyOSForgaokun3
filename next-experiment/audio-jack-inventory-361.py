"""Read existing jack controls only; no UCM changes or capture."""
from pathlib import Path
import json
import runpy
import subprocess

ROOT=Path(__file__).resolve().parents[1]
REMOTE=r'''
from pathlib import Path
import json,re,subprocess
assert Path('/proc/asound/card0/id').read_text().strip()=='SC8280XPHUAWEIG'
rows=[]
for name in ['Headphone Jack','Mic Jack']:
 result=subprocess.run(['amixer','-c','SC8280XPHUAWEIG','cget','name='+name],capture_output=True,text=True,timeout=10)
 match=re.search(r': values=(on|off)\b',result.stdout)
 rows.append(dict(control=name,exit=result.returncode,state=match.group(1) if match else None,stdout=result.stdout,stderr=result.stderr))
print(json.dumps(dict(jacks=rows,controls_modified=False,microphone_recorded=False,headphone_acoustic_output_verified=False),indent=2))
'''
if __name__=='__main__':
 output=ROOT/'reports/audio-jack-inventory-361.json';assert not output.exists()
 ssh=runpy.run_path(str(ROOT/'next-experiment/deploy-settings-data-198.py'))['SSH']
 result=subprocess.run(ssh+['sudo -n python3 -'],input=REMOTE,text=True,capture_output=True,timeout=40)
 assert result.returncode==0,result.stderr
 json.loads(result.stdout);output.open('x').write(result.stdout);print(result.stdout)
