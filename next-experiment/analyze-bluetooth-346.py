"""Keep original-service, HCI acceptance and UI discovery evidence separate."""
from pathlib import Path
import json
import re
import runpy

ROOT=Path(__file__).resolve().parents[1]
open_log=runpy.run_path(str(ROOT/'next-experiment/compress-historical-logs-226.py'))['open_log']

def read(path):
 with open_log(path) as stream:return stream.read().decode(errors='replace')

def fields(line):
 return dict(re.findall(r'([a-z_]+)=([^\s]+)',line))

if __name__=='__main__':
 report=ROOT/'reports/commercial61-native-341'
 output=report/'bluetooth-analysis-346.json'
 assert not output.exists()
 raw=report/'runtime-evidence/raw'
 manifest=json.loads((raw.parent/'retrieval-manifest.json').read_text())
 phases=[name for name in manifest['files'] if re.fullmatch(r'phase-\d+\.log',name)]
 phase_name=max(phases,key=lambda name:int(re.search(r'\d+',name).group()))
 phase=read(raw/phase_name)
 hilog=read(raw/'interactive-hilog030.log')
 launcher=read(raw/'bluetooth339-start.log') if 'bluetooth339-start.log' in manifest['files'] else ''
 pending={};transactions=[];packets={};commands=[]
 for line in phase.splitlines():
  if line.startswith('BT340_SCAN_COMMAND '):
   row=fields(line);commands.append(row);pending.setdefault(row['opcode'],[]).append(row)
  elif line.startswith('BT340_SCAN_STATUS '):
   row=fields(line);queue=pending.setdefault(row['opcode'],[])
   row['request']=queue.pop(0) if queue else None
   transactions.append(row)
  elif line.startswith('BT340_REPORT_PACKETS '):
   row=fields(line);key=row['kind'];packets[key]=max(packets.get(key,0),int(row['count']))
 successful=[row for row in transactions if row['status']=='0' and row['request'] and
   (row['opcode']=='0401' or row['request']['enable']=='1')]
 result=dict(run=manifest['run'],phase_file=phase_name,
   bluetooth_enable_completed='Bluetooth enable event completed' in hilog,
   bluetooth_switch_on='bluetooth switch state is on' in hilog,
   namespace_launcher_context_verified='BT339_CONTEXT namespaces_and_root_verified=1' in launcher,
   original_aa_reported_success='start ability successfully' in launcher.lower(),
   launcher_exit=[fields(line) for line in launcher.splitlines() if line.startswith('BT339_AA_EXIT ')],
   scan_commands=commands,scan_transactions=transactions,
   scan_start_accepted_by_real_controller=bool(successful),
   observed_report_packet_lower_bounds=packets,
   original_ble_scan_request_lines=[i for i,line in enumerate(hilog.splitlines(),1)
      if 'bluetooth_service' in line and '(StartScan:' in line],
   original_classic_discovery_lines=[i for i,line in enumerate(hilog.splitlines(),1)
      if 'bluetooth_service' in line and 'StartBtDiscovery' in line],
   nearby_devices_in_settings_verified=False,pairing_verified=False,
   reconnection_verified=False,low_power_verified=False,
   application_credentials_changed=False,original_permission_checks_changed=False,
   raw_nearby_device_names_or_addresses_exported_by_observer=False,
   disk_validation_suite_rerun=False)
 output.open('x').write(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
