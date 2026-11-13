"""Fresh read-only 045 inventory; no selection or retirement operation."""
from pathlib import Path
import runpy

source = runpy.run_path(str(Path(__file__).with_name('audit-native-efi-space-044.py')))['source']
for old, new in [('native-presentation-044-efi-inventory.json', 'native-presentation-045-efi-inventory.json'),
                 ('native-original-graphics-boot-044', 'native-original-graphics-boot-045')]:
    assert old in source, old
    source = source.replace(old, new)
compile(source, 'inventory-native045', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'inventory-native045', 'exec'), {'__name__': '__main__', '__file__': __file__})
