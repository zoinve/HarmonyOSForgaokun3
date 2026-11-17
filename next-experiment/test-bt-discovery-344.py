from pathlib import Path
import json
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
if __name__=='__main__':
 output=ROOT/'reports/bluetooth-discovery-test-344.json'
 assert not output.exists()
 with tempfile.TemporaryDirectory(prefix='bt340-') as directory:
  binary=Path(directory)/'test'
  subprocess.run(['gcc','-Wall','-Wextra','-Werror','-O1','-g','-fsanitize=address,undefined',
    str(ROOT/'next-experiment/test-bt-discovery-340.c'),'-o',str(binary)],check=True)
  result=subprocess.run([str(binary)],capture_output=True,text=True,check=True,timeout=10)
 data=dict(address_and_undefined_sanitizers_passed=True,stdout=result.stdout,
   hardware_scan_verified=False,command_or_event_translation=False,device_addresses_exported=False)
 output.open('x').write(json.dumps(data,indent=2)+'\n')
 print(json.dumps(data,indent=2))
