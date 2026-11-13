"""Fresh 920: start unchanged original HDC once through normal init."""
from pathlib import Path
import runpy

base = Path(__file__).resolve().parent
transform = runpy.run_path(str(base / 'hdc-start.py'))['hdc_start']
template = (base / 'build-hdc-probe-payload.py').read_text()
old = "source=runpy.run_path(str(base/'hdc-probe.py'))['hdc_probe']((base/'payload-917/init.c').read_text())"
new = "source=transform((base/'payload-919/init.c').read_text())\nsource=source.replace('param get persist.hdc.mode.tcp;', 'param get persist.hdc.mode.usb; param get persist.hdc.mode.tcp;')"
assert template.count(old) == 1
template = template.replace(old, new)
template = template.replace('payload-918', 'payload-920').replace('command-probe-918', 'command-probe-920').replace('hdc-probe-918', 'hdc-start-920')
exec(compile(template, __file__, 'exec'), {'__file__': __file__, 'transform': transform})
