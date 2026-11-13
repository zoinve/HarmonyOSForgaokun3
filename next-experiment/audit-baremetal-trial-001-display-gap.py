"""Read-only comparison of active Ubuntu suppliers and candidate module closure."""
from pathlib import Path
import json
import subprocess

report = Path(__file__).resolve().parent.parent / 'reports/baremetal-native-trial-001-display-gap.json'
assert not report.exists()
payload = r'''
from pathlib import Path
import json,subprocess,shutil
root=Path('/mnt/harmony-lab/work/native-module-root-001')
release='7.1.0-rc3-gaokun3-el2'
config=Path('/mnt/harmony-lab/work/native-build-001/artifacts/.config').read_text().splitlines()
keys=['CONFIG_SC_DISPCC_8280XP=','CONFIG_SC_GPUCC_8280XP=','CONFIG_PHY_QCOM_QMP_COMBO=']
rows=[]
for device in Path('/sys/bus/platform/devices').iterdir():
 if device.name not in ['af00000.clock-controller','3d90000.clock-controller','88eb000.phy','8903000.phy']:continue
 driver=device/'driver';alias=device/'modalias'
 rows.append(dict(device=device.name,driver=driver.resolve().name if driver.exists() else None,
  module=(driver/'module').resolve().name if (driver/'module').exists() else None,
  alias=alias.read_text().strip() if alias.is_file() else None))
checks=[]
for name in ['dispcc_sc8280xp','gpucc_sc8280xp','phy_qcom_qmp_combo']:
 p=subprocess.run([shutil.which('modprobe') or '/usr/sbin/modprobe','--dirname',str(root),
  '--set-version',release,'--config',str(root/'etc/modprobe.d'),'--show-depends',name],
  capture_output=True,text=True,timeout=10)
 checks.append(dict(module=name,returncode=p.returncode,stdout=p.stdout,stderr=p.stderr))
print(json.dumps(dict(running_kernel=subprocess.check_output(['uname','-r'],text=True).strip(),
 candidate_config=[l for l in config if any(l.startswith(k) for k in keys)],
 active_suppliers=rows,offline_dependencies=checks,modules_loaded=False,
 boot_entries_modified=False,reboot_requested=False),indent=2))
'''
p = subprocess.run(['ssh', 'matebook', 'python3 -'], input=payload,
                   text=True, capture_output=True, timeout=90)
p.check_returncode()
result = json.loads(p.stdout)
report.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2))
