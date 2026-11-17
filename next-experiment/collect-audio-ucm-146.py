"""Read Ubuntu's installed board ALSA configuration; never change controls."""
from pathlib import Path
import datetime
import json
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
PAYLOAD = r'''
from pathlib import Path
import hashlib,json,os
root=Path('/usr/share/alsa').resolve(strict=True)
selected=[]
for index,path in enumerate(root.rglob('*.conf')):
 assert index<10000,'refusing unbounded configuration walk'
 relative=str(path.relative_to(root))
 lower=relative.lower()
 if not (relative=='alsa.conf' or any(name in lower for name in ['sc8280','gaokun','wcd938','wsa883']) or relative.startswith('ucm2/lib/')):continue
 real=path.resolve(strict=True)
 assert real.is_relative_to(root),('configuration link escaped ALSA root',relative)
 assert real.is_file()
 with real.open('rb') as stream:data=stream.read(65537)
 assert len(data)<=65536,('configuration too large',relative)
 selected.append(dict(path=relative,resolved=str(real.relative_to(root)),bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),content=data.decode('utf-8')))
 assert len(selected)<=128,'refusing excessive configuration export'
assert sum(row['bytes'] for row in selected)<=1048576
board_mapping=any('gaokun' in row['path'].lower() for row in selected)
print(json.dumps(dict(context='Ubuntu installed configuration, not native playback or HDI acceptance',kernel=os.uname().release,files=selected,board_specific_mapping_present=board_mapping,read_only=True,controls_changed=False,audio_recorded=False)))
'''


if __name__ == '__main__':
    runpy.run_path(str(BASE / 'commercial-workflow-145.py'))['configure_local_transport']()
    result = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
        '-o', 'ConnectTimeout=8', '-o', 'HostName=192.168.10.128', '-o', 'HostKeyAlias=192.168.10.128',
        'matebook', 'python3 -'], input=PAYLOAD, text=True, capture_output=True, timeout=60)
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    report = BASE.parent / 'reports' / ('audio-ucm-146-' + stamp)
    report.mkdir()
    (report / 'result.json').open('x').write(json.dumps(data, indent=2))
    print(json.dumps(dict(report=str(report.relative_to(BASE.parent)),files=[row['path'] for row in data['files']],board_specific_mapping_present=data['board_specific_mapping_present'],read_only=True),indent=2))
