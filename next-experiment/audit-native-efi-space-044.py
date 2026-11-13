"""Fresh read-only inventory for 044; never select, retire or rewrite an entry."""
from pathlib import Path

source = Path(__file__).with_name('audit-native-efi-space-043.py').read_text()
source = source.replace('native-presentation-043-efi-inventory.json', 'native-presentation-044-efi-inventory.json')
source = source.replace('native-original-graphics-boot-043', 'native-original-graphics-boot-044')
compile(source, 'inventory-native044', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'inventory-native044', 'exec'), {'__name__': '__main__', '__file__': __file__})
