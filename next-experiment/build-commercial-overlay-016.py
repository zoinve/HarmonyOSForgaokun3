"""Only own board drivers/harness over immutable commercial 001; exact members."""
from pathlib import Path
import runpy,subprocess
payload=runpy.run_path(str(Path(__file__).with_name('build-commercial-overlay-010.py')))['payload']
payload=payload.replace('commercial61-native-010','commercial61-native-016-r2')
start=payload.index('assert set(new)-set(old)==')
end=payload.index("data=b''.join",start)
checks=r'''
bundle=json.loads((root/'commercial-graphics-bundle-016/result.json').read_text())
hardware={'native-target/graphics016'+item['target'] for item in bundle['files']}
helpers={'native-target/samgr-observe','native-target/samgr_standard005.cfg','native-target/sandbox-system008.json','native-target/sandbox-chipset008.json'}
assert set(new)-set(old)==helpers|hardware and not set(old)-set(new)
changed={n for n in new if old.get(n)!=new[n]}
assert changed==helpers|hardware|{'init','native-target/bootstrap'},changed
for item in bundle['files']:
 assert hashlib.sha256(new['native-target/graphics016'+item['target']][1]).hexdigest()==item['sha256']
'''
payload=payload[:start]+checks+payload[end:]
payload=payload.replace('commercial_libraries_unchanged=True','original_images_unchanged=True,original_service_binaries_unchanged=True,own_hardware_drivers_added=True')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True,timeout=120).returncode)
