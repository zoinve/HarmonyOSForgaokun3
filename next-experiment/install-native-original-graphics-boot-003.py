"""Install 003; reclaim only unreferenced EFI caches with preserved originals."""
from pathlib import Path
import subprocess
import json
source=Path(__file__).with_name('install-native-original-graphics-boot-001.py').read_text()
source=source.replace('native-original-graphics-boot-001','native-original-graphics-boot-003')
source=source.replace('native-original-graphics-001','native-original-graphics-003')
source=source.replace('native trial 001','native trial 003')
source=source.replace("['009','010']","['008','014']")
source=source.replace('and sha(p)==sha(kernel)', '''and sha(p)==(
   '8ba8c0049c3608e3a72769897e718051c78addb4d73a29699714f2e49f576457'
   if p.parent.name=='harmony-native-diag-008' else sha(kernel))''')
source=source.replace('retained_identical_kernel=str(kernel)',
    "retained_identical_kernel=str(kernel),retained_008_original='/home/zoinve/harmony-virgl-883/baremetal-identity-native-package-001/linux (WSL Debian)'")
if __name__=='__main__':
    # Independently verify the older kernel's ORIGINAL build artifact before
    # removing its obsolete EFI cache, which differs from the current kernel.
    check="import hashlib;from pathlib import Path;p=Path('/home/zoinve/harmony-virgl-883/baremetal-identity-native-package-001/linux');assert p.is_file() and not p.is_symlink();print(hashlib.file_digest(p.open('rb'),'sha256').hexdigest())"
    h=subprocess.check_output(['wsl','-d','Debian','--','python3','-c',check],text=True).strip()
    assert h=='8ba8c0049c3608e3a72769897e718051c78addb4d73a29699714f2e49f576457'
    evidence=Path(__file__).resolve().parent.parent/'reports/native-original-graphics-boot-003/retained-kernel-source.json'
    with evidence.open('x') as f:json.dump(dict(sha256=h,original_build_preserved=True),f)
    exec(compile(source,__file__,'exec'),{'__name__':'__main__','__file__':__file__})
