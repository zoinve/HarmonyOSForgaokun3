"""Correlate preserved native lifecycle logs after the delayed query returns."""
from pathlib import Path

BASE = Path(__file__).resolve().parent
source = (BASE / 'analyze-original-devicedetect-095.py').read_text()
source = source.replace('original-devicedetect-095.json', 'original-oobe-lifecycle-095.json')
source = source.replace("collabfwk|devicedetect|device.?detect|cfwk|devicepicker|CollaborationFwk",
    "BaseOobeManager|sessionExceptionCallback|start oobe|provisioned|setup.*complete|onKeyEvent|KEYCODE|CloseWindow|close.*oobe|oobe.*close|Dock.*(?:ready|complete)|SCBDesktop.*(?:show|hide)|guide.*(?:foreground|background)|(?:foreground|background).*guide")
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
