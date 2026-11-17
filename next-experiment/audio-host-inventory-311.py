"""Read public Ubuntu audio capabilities; do not activate routes or record sound."""
from pathlib import Path
import json
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
QUERY = r'''
from pathlib import Path
import json,shutil,subprocess
release=subprocess.check_output(['uname','-r'],text=True).strip()
assert release=='7.1.0-rc3-gaokun3+'
files={}
for name in ['/proc/asound/cards','/proc/asound/pcm','/proc/asound/card0/id',
 '/proc/asound/card0/pcm0p/sub0/hw_params','/proc/asound/card0/pcm1p/sub0/hw_params']:
 path=Path(name)
 if path.is_file():
  with path.open('r') as stream:files[name]=stream.read(4096)
ucm=[]
root=Path('/usr/share/alsa/ucm2')
if root.is_dir():
 for pattern in ['Qualcomm/sc8280xp/*','Qualcomm/*gaokun*','conf.d/sc8280xp/*','conf.d/SC8280XP*/*']:
  for path in root.glob(pattern):
   ucm.append(dict(path=str(path),resolved=str(path.resolve()),is_file=path.is_file()))
library=Path('/usr/lib/aarch64-linux-gnu/libasound.so.2')
print(json.dumps(dict(kernel=release,files=files,ucm_paths=ucm,
 tools={name:shutil.which(name) for name in ['aplay','amixer','alsaucm','tinymix']},
 alsa_library=str(library.resolve()) if library.is_file() else None,
 routes_modified=False,playback_started=False,microphone_recorded=False,
 harmony_audio_acceptance=False),indent=2))
'''

if __name__ == '__main__':
    output=ROOT/'reports/audio-host-inventory-311.json'
    assert not output.exists()
    ssh=runpy.run_path(str(ROOT/'next-experiment/deploy-settings-data-198.py'))['SSH']
    result=subprocess.run(ssh+['python3 -'],input=QUERY,text=True,capture_output=True,timeout=25)
    assert result.returncode==0,result.stderr
    json.loads(result.stdout)
    output.open('x').write(result.stdout)
    print(result.stdout)
