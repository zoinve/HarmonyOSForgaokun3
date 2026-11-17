"""Read actual Ubuntu radio backends and public model fields, never identities."""
from pathlib import Path
import datetime
import json
import runpy
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/wireless-device-257'
PAYLOAD = r'''
from pathlib import Path
import json
def text(path):
    try: return Path(path).read_text().strip().replace('\x00', '')
    except OSError: return None
def driver(path):
    p=Path(path)/'device/driver'
    return p.resolve().name if p.exists() else None
fields=('sys_vendor','product_name','product_version','board_vendor','board_name','board_version')
result=dict(kernel=text('/proc/sys/kernel/osrelease'),
    public_dmi={k:text('/sys/class/dmi/id/'+k) for k in fields},
    device_tree_model=text('/sys/firmware/devicetree/base/model'),
    rfkill=[dict(node=p.name, **{k:text(p/k) for k in ('name','type','soft','hard')})
        for p in sorted(Path('/sys/class/rfkill').glob('rfkill*'))],
    wifi=[dict(interface=p.name,driver=driver(p),operstate=text(p/'operstate'))
        for p in sorted(Path('/sys/class/net').iterdir()) if (p/'phy80211').exists()],
    bluetooth=[dict(controller=p.name,type=text(p/'type'),driver=driver(p))
        for p in sorted(Path('/sys/class/bluetooth').glob('hci*'))],
    modules=[line.split()[0] for line in Path('/proc/modules').read_text().splitlines()
        if line.split()[0] in ('ath11k_pci','ath11k','hci_uart','btqca','bluetooth')],
    context='Ubuntu backend enumeration, not HarmonyOS service acceptance',
    target_modified=False,credentials_or_unique_identifiers_collected=False)
print(json.dumps(result))
'''


if __name__ == '__main__':
    assert not REPORT.exists(), 'preserve numbered evidence'
    ssh = runpy.run_path(str(ROOT / 'next-experiment/deploy-settings-data-198.py'))['SSH']
    proc = subprocess.run(ssh + ['python3 -'], input=PAYLOAD, text=True,
                          capture_output=True, timeout=20)
    if proc.returncode:
        raise SystemExit(f'Ubuntu read-only collection unavailable: SSH exit {proc.returncode}')
    result = json.loads(proc.stdout)
    result['observed_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result['user_confirmed_settings_accessible'] = True
    result['priority'] = ['bluetooth_enable', 'wifi_scan', 'actual_device_display_information']
    REPORT.mkdir()
    (REPORT / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
