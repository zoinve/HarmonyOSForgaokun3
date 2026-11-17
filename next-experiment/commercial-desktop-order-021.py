"""Use the reference's ordinary aa argv, not 020's unsupported user-ID option."""
from pathlib import Path
import runpy

def repair(original):
    patched=runpy.run_path(str(Path(__file__).with_name('commercial-desktop-order-020.py')))['repair'](original)
    command='/usr/bin/aa start -b com.ohos.sceneboard -a com.ohos.sceneboard.MainAbility -m pc_sceneboard -u 100'
    assert patched.count(command)==1
    patched=patched.replace(command,command.removesuffix(' -u 100'),1)
    patched=patched.replace('COMMERCIAL020_SCENEBOARD','COMMERCIAL021_SCENEBOARD').replace('user_id=100','user_selection=aa_default')
    patched=patched.replace('# User 100 is the real STANDARD account created by the original Account Manager.\n# Selecting it through aa does not activate it or bypass any authorization.','# Preserve the original aa user-selection behavior and all authorization checks.')
    return patched
