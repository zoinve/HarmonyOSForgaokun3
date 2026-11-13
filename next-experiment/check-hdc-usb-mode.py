from pathlib import Path
import runpy
base=Path(__file__).resolve().parent
source=(base/'payload-918/init.c').read_text()
transform=runpy.run_path(str(base/'hdc-usb-mode.py'))['hdc_usb_mode']
result=transform(source)
added=r'\"setparam persist.hdc.mode.usb disable\", '
assert result.count(added)==1
assert result.replace(added,'')==source
assert 'setparam const.hdc.secure' not in result
print('PASS: only completes original transport trigger; all identity/auth settings preserved')
