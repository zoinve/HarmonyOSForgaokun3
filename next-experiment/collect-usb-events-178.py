"""Collect allowlisted USB kernel events without exporting raw journal messages."""
from pathlib import Path
import datetime
import json
import runpy
import subprocess

BASE = Path(__file__).resolve().parent


def parse_event(message):
    import re
    prefix = re.search(r'\busb (\d+-\d+(?:\.\d+)*): (.*)', message)
    if not prefix:
        return None
    route, body = prefix.groups()
    kinds = [
        ('identity', r'New USB device found, idVendor=([0-9a-fA-F]{4}), idProduct=([0-9a-fA-F]{4})'),
        ('disconnect', r'USB disconnect, device number (\d+)'),
        ('connect', r'new (?:(?:low|full|high)-speed|SuperSpeed(?: Plus)?(?: Gen \d+x\d+)?) USB device number (\d+)'),
        ('reset', r'reset .* USB device number (\d+)'),
        ('descriptor_error', r'device descriptor .* error (-?\d+)'),
        ('address_error', r'device not accepting address \d+, error (-?\d+)'),
        ('enumeration_error', r'unable to enumerate USB device'),
        ('setup_error', r'(?:Cannot enable|cannot reset|Device not responding to setup address)'),
    ]
    for kind, pattern in kinds:
        match = re.match(pattern, body)
        if match:
            row = dict(route=route, kind=kind)
            if kind == 'identity':
                row.update(vid=match[1].lower(), pid=match[2].lower())
            elif kind in ['disconnect', 'connect', 'reset']:
                row['device_number'] = int(match[1])
            elif kind in ['descriptor_error', 'address_error']:
                row['errno'] = int(match[1])
            return row
    return None


def payload():
    import inspect
    return 'import json,re,subprocess\nfrom pathlib import Path\n' + inspect.getsource(parse_event) + r'''
result=[]
pattern=r'usb [0-9]+-[0-9.]+: (New USB device found|USB disconnect|new |reset |device descriptor|device not accepting|unable to enumerate|Cannot enable|cannot reset|Device not responding)'
for boot in ['0','-1','-2']:
    proc=subprocess.run(['journalctl','--kernel','--boot='+boot,'--no-pager','--output=json',
        '--output-fields=MESSAGE,__MONOTONIC_TIMESTAMP,_BOOT_ID','--grep='+pattern],
        capture_output=True,text=True,timeout=25)
    events=[]
    if proc.returncode==0:
        for line in proc.stdout.splitlines():
            item=json.loads(line)
            message=item.get('MESSAGE')
            if not isinstance(message,str):continue
            event=parse_event(message)
            if event is not None:
                event['monotonic_us']=int(item['__MONOTONIC_TIMESTAMP'])
                event['boot_id']=item['_BOOT_ID']
                events.append(event)
    diagnostics=[]
    for marker,label in [('No entries','no_entries'),('No journal files','no_journal_files'),
                         ('unrecognized option','unsupported_option'),('Failed to','journal_query_failed')]:
        if marker in proc.stderr:diagnostics.append(label)
    result.append(dict(boot_offset=int(boot),journal_returncode=proc.returncode,
        diagnostic_kinds=diagnostics,events=events))
proc=subprocess.run(['dmesg','--color=never'],capture_output=True,text=True,timeout=15)
events=[]
boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
if proc.returncode==0:
    for line in proc.stdout.splitlines():
        event=parse_event(line)
        if event is not None:
            timestamp=re.match(r'\[\s*(\d+)\.(\d+)\]',line)
            if timestamp:event['monotonic_us']=int(timestamp[1])*1000000+int(timestamp[2].ljust(6,'0')[:6])
            event['boot_id']=boot_id
            events.append(event)
print(json.dumps(dict(boots=result,dmesg=dict(returncode=proc.returncode,events=events),
    raw_messages_exported=False,serials_exported=False,
    input_events_read=False,target_modified=False)))
'''


if __name__ == '__main__':
    runpy.run_path(str(BASE / 'commercial-workflow-175.py'))['configure_local_transport']()
    proc = subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
        '-o', 'ConnectTimeout=8', '-o', 'HostName=192.168.10.128', '-o', 'HostKeyAlias=192.168.10.128',
        'matebook', 'sudo -n python3 -'], input=payload(), text=True, capture_output=True, timeout=100)
    assert proc.returncode == 0, 'sanitized USB journal collector failed'
    data = json.loads(proc.stdout)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    report = BASE.parent / 'reports' / ('usb-events-178-' + stamp)
    report.mkdir()
    (report / 'result.json').open('x').write(json.dumps(data, indent=2))
    print(json.dumps(dict(report=str(report.relative_to(BASE.parent)), **data), indent=2))
