from pathlib import Path
import runpy,subprocess
base=Path(__file__).resolve().parent;p=base/'build-native-original-graphics-boot-026.py'
assert p.exists(),'missing input/settings native candidate'
d=runpy.run_path(str(p))
for token in ('phy_qcom_snps_femto_v2','phy_qcom_qmp_usb','hid_multitouch'):
    assert token in d['outer']
for token in ('NATIVE_INPUT026','/proc/bus/input/devices','com.huawei.hmos.settings.MainAbility'):
    assert token in d['inner']
payload=runpy.run_path(str(base/'test-native-original-graphics-boot-001.py'))['payload'].replace('native-original-graphics-boot-001','native-original-graphics-boot-026')
if __name__=='__main__':raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True).returncode)
