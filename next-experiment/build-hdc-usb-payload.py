"""Fresh 919: complete both inputs to the unchanged native HDC trigger."""
from pathlib import Path
import runpy
base=Path(__file__).resolve().parent
transform=runpy.run_path(str(base/'hdc-usb-mode.py'))['hdc_usb_mode']
source=(base/'build-hdc-probe-payload.py').read_text()
old="source=runpy.run_path(str(base/'hdc-probe.py'))['hdc_probe']((base/'payload-917/init.c').read_text())"
new="source=transform((base/'payload-918/init.c').read_text())"
assert source.count(old)==1
source=source.replace(old,new).replace('payload-918','payload-919').replace('command-probe-918','command-probe-919').replace('hdc-probe-918','hdc-usb-919')
# The input is immutable 918, not the new output directory.
source=source.replace("transform((base/'payload-919/init.c')", "transform((base/'payload-918/init.c')")
exec(compile(source,__file__,'exec'),{'__file__':__file__,'transform':transform})
