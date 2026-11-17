"""Separate source callbacks, original-service playback, real PCM and acoustics."""
from pathlib import Path
import json
import re
import runpy

ROOT=Path(__file__).resolve().parents[1]
open_log=runpy.run_path(str(ROOT/'next-experiment/compress-historical-logs-226.py'))['open_log']
def read(path):
 with open_log(path) as stream:return stream.read().decode(errors='replace')
def records(text,marker):
 result=[]
 for number,line in enumerate(text.splitlines(),1):
  if line.startswith(marker+' '):
   row=dict(re.findall(r'([a-z_]+)=([^\s]+)',line))
   row={key:int(value) if re.fullmatch(r'-?\d+',value) else value for key,value in row.items()}
   result.append(dict(line=number,**row))
 return result

if __name__=='__main__':
 report=ROOT/'reports/commercial61-native-353';output=report/'audio-analysis-357.json'
 assert not output.exists()
 raw=report/'runtime-evidence/raw'
 manifest=json.loads((raw.parent/'retrieval-manifest.json').read_text())
 phases=[name for name in manifest['files'] if re.fullmatch(r'phase-\d+\.log',name)]
 phase_name=max(phases,key=lambda name:int(re.search(r'\d+',name).group()))
 phase=read(raw/phase_name);hilog=read(raw/'interactive-hilog030.log')
 helper=read(raw/'audio351-renderer.log') if 'audio351-renderer.log' in manifest['files'] else ''
 metrics=records(phase,'AUDIO349_ACCEPTED')
 steps=records(helper,'AUDIO350_STEP');states=records(helper,'AUDIO350_STATE')
 ends=records(helper,'AUDIO350_END');io=records(phase,'AUDIO316_IO')
 accepted=sum(row['frames'] for row in metrics)
 nonzero=sum(row['nonzero_frames'] for row in metrics)
 first=next((row for row in states if row['stage']=='first_running'),None)
 resumed=next((row for row in states if row['stage']=='resumed_running'),None)
 advanced=bool(first and resumed and first['timestamp_code']==0 and resumed['timestamp_code']==0
    and resumed['position']>first['position'])
 result=dict(run=manifest['run'],phase_file=phase_name,
   original_render_created='create render success, hdiRenderId_' in hilog,
   real_pcm_ready='AUDIO316_PCM_READY rate=48000 channels=2 format=S16_LE' in phase,
   accepted_playback=metrics,total_accepted_frames=accepted,total_nonzero_frames=nonzero,
   nonzero_samples_accepted_by_real_alsa=nonzero>0,
   total_operation_error_replies=sum(row['operation_errors'] for row in metrics),
   helper_namespace_verified='AUDIO351_CONTEXT namespaces_and_root_verified=1' in helper,
   public_api_steps=steps,public_api_failures=[row for row in steps if row['code']],
   public_api_states=states,public_api_ends=ends,
   public_api_helper_completed=bool(ends and ends[-1]['result']==0),
   timestamp_position_advanced_after_resume=advanced,
   logged_pcm_playback_position_advanced=any(row.get('played',0)>0 for row in io),
   backend_transport_termination=records(phase,'AUDIO329_TRANSPORT'),
   bluetooth_enable_completed='Bluetooth enable event completed' in hilog,
   bluetooth_report_packet_counters=records(phase,'BT340_REPORT_PACKETS'),
   touch=records(phase,'TOUCH303_END'),audio_broker_exit=records(phase,'AUDIO321_BROKER'),
   physical_multitouch_verified=False,application_gestures_verified=False,
   acoustic_output_verified=False,microphone_recorded=False,headphones_verified=False,
   refresh_120hz_verified=False,credentials_changed=False,permission_checks_changed=False,
   original_images_modified=False,active165_modified=False,disk_validation_suite_rerun=False)
 output.open('x').write(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
