from pathlib import Path
import json
import re
import runpy

ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
 report=ROOT/'reports/commercial61-native-306'
 output=report/'driver-analysis-313.json'
 assert not output.exists()
 evidence=report/'runtime-evidence'
 manifest=json.loads((evidence/'retrieval-manifest.json').read_text())
 phases=[name for name in manifest['files'] if re.fullmatch(r'phase-\d+\.log',name)]
 phase=max(phases,key=lambda name:int(name[6:-4]))
 reader=runpy.run_path(str(ROOT/'next-experiment/compress-historical-logs-226.py'))['open_log']
 with reader(evidence/'raw'/phase) as stream:text=stream.read().decode(errors='replace')
 with reader(evidence/'raw/interactive-hilog030.log') as stream:hilog=stream.read().decode(errors='replace')
 end=re.findall(r'TOUCH303_END result=(\d+) frames=(\d+) max_concurrent=(\d+) dropped=(\d+) physical_multicontact_observed=(\d+) app_delivery_verified=(\d+)',text)
 assert len(end)==1
 error,frames,maximum,dropped,observed,delivered=map(int,end[0])
 result=dict(run=manifest['run'],phase=phase,
  bluetooth=dict(original_enable_completed='Bluetooth enable event completed' in hilog,
   original_switch_on='bluetooth switch state is on' in hilog,
   power_on_failures=hilog.count('vendorInterface_->op BT_OP_POWER_ON failed.'),
   real_channel_opens=text.count('NATIVE_QCA022 real_channel_open=1'),
   discovery_verified=False,pairing_verified=False,low_power_verified=False),
  touch=dict(observer_exit=error,frames=frames,max_concurrent=maximum,dropped=dropped,
   slots=10 if 'slots=10 read_only=1 grab=0 injection=0' in text else None,
   monitor_reaped_cleanly='TOUCH306_MONITOR_END forced_stop=0 raw_wait_status=0' in text,
   physical_multicontact_observed=bool(observed and not dropped and not error),
   application_delivery_verified=bool(delivered),
   events_injected=False,original_mmi_modified=False),
  audio_playback_verified=False,refresh_120hz_verified=False)
 output.open('x').write(json.dumps(result,indent=2))
 print(json.dumps(result,indent=2))
