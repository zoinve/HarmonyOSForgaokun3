"""Inspect original product defaults and constants without changing the HAP."""
from pathlib import Path

base = Path(__file__).resolve().parent
source = (base / 'audit-commercial-dock-flow-086.py').read_text()
anchor = "'/DefaultLayoutConfig&1.0.0;', '/LayoutConfigManager&1.0.0;')"
assert source.count(anchor) == 1
source = source.replace(anchor,
    "'/DefaultLayoutConfig&1.0.0;', '/LayoutConfigManager&1.0.0;', "
    "'/PresetDockItem&1.0.0;', '/constants/CommonConstants&1.0.0;', "
    "'/bean/DockItemInfo&1.0.0;')", 1)
source = source.replace('commercial-dock-flow-audit-086',
                        'commercial-dock-defaults-audit-086-revision3')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
