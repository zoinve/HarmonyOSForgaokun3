"""Extend the read-only Dock audit to its original external config loaders."""
from pathlib import Path

b = Path(__file__).resolve().parent
source = (b / 'audit-commercial-dock-flow-086.py').read_text()
anchor = "'/DefaultLayoutConfig&1.0.0;', '/LayoutConfigManager&1.0.0;')"
assert source.count(anchor) == 1
source = source.replace(anchor, "'/DefaultLayoutConfig&1.0.0;', '/LayoutConfigManager&1.0.0;', '/GetLayoutInfoFromConfig&1.0.0;', '/DesktopDataLoader&1.0.0;', '/PcDesktopDataLoader&1.0.0;')", 1)
source = source.replace('commercial-dock-flow-audit-086', 'commercial-dock-loader-audit-086-revision2')
if __name__ == '__main__':
    exec(compile(source, __file__, 'exec'), {'__name__': '__main__', '__file__': __file__})
