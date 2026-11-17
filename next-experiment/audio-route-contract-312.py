"""Inspect deployed UCM definitions and mixer names without changing controls."""
from pathlib import Path
import json
import runpy
import subprocess

ROOT=Path(__file__).resolve().parents[1]
QUERY=r'''
from pathlib import Path
import json,subprocess
files={}
for name in ['sc8280xp.conf','HiFi.conf','LENOVO-X13s.conf']:
 path=Path('/usr/share/alsa/ucm2/Qualcomm/sc8280xp')/name
 assert path.is_file() and path.stat().st_size<65536
 files[str(path)]=path.read_text()
controls=subprocess.run(['amixer','-c','0','scontrols'],capture_output=True,text=True,timeout=12)
assert controls.returncode==0,controls.stderr
print(json.dumps(dict(ucm_definitions=files,simple_mixer_controls=controls.stdout,
 controls_modified=False,speaker_activated=False,microphone_activated=False,
 host_observation_only=True),indent=2))
'''

if __name__=='__main__':
 output=ROOT/'reports/audio-route-contract-312.json'
 assert not output.exists()
 ssh=runpy.run_path(str(ROOT/'next-experiment/deploy-settings-data-198.py'))['SSH']
 result=subprocess.run(ssh+['sudo -n python3 -'],input=QUERY,text=True,capture_output=True,timeout=25)
 assert result.returncode==0,result.stderr
 evidence=json.loads(result.stdout)
 output.open('x').write(result.stdout)
 print(json.dumps(evidence,indent=2))
