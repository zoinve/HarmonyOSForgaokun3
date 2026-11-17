"""Exercise real read-only readiness and short-alias length checks, never install."""
from pathlib import Path
import datetime
import json
import runpy
import subprocess

BASE = Path(__file__).resolve().parent

if __name__ == '__main__':
    api = runpy.run_path(str(BASE / 'commercial-workflow-176.py'))
    overlay = json.loads((api['REPORT'] / 'overlay-result.json').read_text())
    assert overlay['chain'][-1] == 'commercial61-native-176/initrd.img'
    code = 'from pathlib import Path\nimport json\nchain=' + repr(overlay['chain'][:-1] + ['usb176.img']) + '\n'
    code += 'usb_ready=True\ntry:\n' + ''.join(' ' + line + '\n' for line in api['USB_PREFLIGHT'].splitlines())
    code += '''except AssertionError:
 usb_ready=False
esp=Path('/boot/efi')
old=(esp/'loader/entries/harmonyos-gpu-manual.conf').read_text()
options=next(line for line in old.splitlines() if line.startswith('options ')).replace('panic=0','panic=15')+' harmony.commercial=1 harmony.live_debug159=1 harmony.persistent_data166=1 harmony.usb_readonly175=1'
assert options.count('rdinit=/init ')==1
options=options.replace('rdinit=/init ','rdinit=/early-hardware093.sh ',1)
estimated=len(options[8:])+sum(len('initrd=\\\\'+path.replace('/','\\\\'))+1 for path in chain)+1
print(json.dumps(dict(usb_ready=usb_ready,estimated_options_bytes=estimated,
 command_line_within_existing_bound=estimated<1800,
 working173_entry_present=(esp/'loader/entries/commercial61-native-173.conf').is_file(),
 candidate176_entry_present=(esp/'loader/entries/commercial61-native-176.conf').exists(),
 candidate176_alias_present=(esp/'usb176.img').exists(),
 target_modified=False,reboot_requested=False)))
'''
    compile(code, 'readiness176-remote', 'exec')
    api['configure_local_transport']()
    proc = subprocess.run(['ssh','-o','BatchMode=yes','-o','StrictHostKeyChecking=yes',
        '-o','ConnectTimeout=8','-o','HostName=192.168.10.128','-o','HostKeyAlias=192.168.10.128',
        'matebook','sudo -n python3 -'], input=code, text=True, capture_output=True, timeout=45)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    report = api['REPORT'] / ('readiness-' + stamp)
    report.mkdir()
    (report / 'remote.py').open('x').write(code)
    if proc.returncode:
        failure=dict(returncode=proc.returncode,target_modified=False,
                     collection_succeeded=False)
        (report / 'failure.json').open('x').write(json.dumps(failure,indent=2))
        raise SystemExit('read-only readiness collection failed; no install or reboot')
    result = json.loads(proc.stdout)
    (report / 'result.json').open('x').write(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
