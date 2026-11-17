"""Summarize original services and actual PCM evidence without acceptance inflation."""
from pathlib import Path
import json
import re
import runpy
import sys

ROOT=Path(__file__).resolve().parents[1]
open_log=runpy.run_path(str(ROOT/'next-experiment/compress-historical-logs-226.py'))['open_log']

def analyze(candidate):
 report=ROOT/'reports'/('commercial61-native-'+candidate)
 output=report/'audio-analysis-336.json'
 assert not output.exists()
 raw=report/'runtime-evidence/raw'
 with open_log(raw/'phase-181.log') as stream:
  phase=stream.read().decode(errors='replace')
 with open_log(raw/'interactive-hilog030.log') as stream:
  hilog=stream.read().decode(errors='replace')
 def records(marker):
  return [dict((key,int(value)) for key,value in re.findall(r'([a-z_]+)=(-?\d+)',line))
    for line in phase.splitlines() if line.startswith(marker+' ')]
 io=records('AUDIO316_IO')
 ends=records('AUDIO316_STREAM_END')
 touches=records('TOUCH303_END')
 result=dict(candidate=candidate,
  original_render_created='create render success, hdiRenderId_' in hilog,
  real_pcm_ready='AUDIO316_PCM_READY rate=48000 channels=2 format=S16_LE' in phase,
  logged_transactions=len(io),
  logged_io_errors=[row for row in io if row.get('result')],
  logged_playback_position_advanced=any(row.get('played',0)>0 for row in io),
  logged_accounting_consistent=bool(io) and all(row['submitted']==row['played']+row['delay'] for row in io if row['result']==0),
  streams=ends,submitted_frames_at_stream_end=sum(row.get('submitted',0) for row in ends),
  later_transactions_not_fully_logged=True,
  transport_termination=records('AUDIO329_TRANSPORT'),
  bluetooth_enable_completed='Bluetooth enable event completed' in hilog,
  bluetooth_switch_on='bluetooth switch state is on' in hilog,
  touch=touches,
  acoustic_output_verified=False,nonzero_samples_verified=False,
  physical_multitouch_verified=False,application_gestures_verified=False,
  bluetooth_pairing_verified=False,microphone_supported=False,
  headphones_verified=False,refresh_120hz_verified=False,
  source_images_modified=False,disk_validation_suite_rerun=False)
 output.open('x').write(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))

if __name__=='__main__':
 assert len(sys.argv)==2 and sys.argv[1] in ['321','331']
 analyze(sys.argv[1])
