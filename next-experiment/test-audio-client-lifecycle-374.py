from pathlib import Path
import json
import runpy
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'next-experiment'
if __name__=='__main__':
 output=ROOT/'reports/audio-client-lifecycle-374.json';assert not output.exists()
 source=runpy.run_path(str(BASE/'native-audio-vdi-363.py'))['vendor363']()
 with tempfile.TemporaryDirectory(prefix='audio373-') as directory:
  stage=Path(directory);(stage/'vendor.c').open('x').write(source)
  headers=Path('/home/zoinve/harmony-virgl-883/audio-contract-314-peripheral/audio/interfaces/sound/v1_0')
  program=stage/'test'
  subprocess.run(['gcc','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
    '-I',str(stage),'-I',str(BASE),'-I',str(headers),str(BASE/'test-audio-client-lifecycle-373.c'),
    '-pthread','-lm','-o',str(program)],check=True)
  result=subprocess.run([str(program)],capture_output=True,text=True,check=True,timeout=15)
 data=dict(sanitizers_passed=True,stdout=result.stdout,hardware_acceptance=False)
 output.open('x').write(json.dumps(data,indent=2)+'\n');print(json.dumps(data,indent=2))
