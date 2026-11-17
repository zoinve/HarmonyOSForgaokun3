"""Record firmware differences explicitly while checking all other preservation guards."""
from pathlib import Path
import runpy

BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
REPORT=ROOT/'reports/commercial61-native-206'
if __name__=='__main__':
    assert not (REPORT/'post-return-inspection-213.json').exists()
    source=(REPORT/'verify-commercial-return.generated.py').read_text()
    old="assert subprocess.check_output(['efibootmgr','-v'],text=True)==j['firmware']"
    new="firmware_now=subprocess.check_output(['efibootmgr','-v'],text=True)\nfirmware_same=firmware_now==j['firmware']\nfirmware_removed=[line for line in j['firmware'].splitlines() if line not in firmware_now.splitlines()]\nfirmware_added=[line for line in firmware_now.splitlines() if line not in j['firmware'].splitlines()]"
    assert source.count(old)==1 and source.count('firmware_unchanged=True')==1
    source=source.replace(old,new,1).replace('firmware_unchanged=True',
        'firmware_unchanged=firmware_same,firmware_removed_lines=firmware_removed,firmware_added_lines=firmware_added',1)
    source=source.replace('post-return-verification.json','post-return-inspection-213.json')
    (REPORT/'inspect-preservation-213.generated.py').open('x').write(source)
    runpy.run_path(str(BASE/'commercial-workflow-206.py'))['configure_local_transport']()
    exec(compile(source,str(__file__),'exec'),{'__name__':'__main__','__file__':str(__file__)})
