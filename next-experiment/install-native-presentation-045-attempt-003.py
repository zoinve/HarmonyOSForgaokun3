"""Use validated historical base text without recreating or editing old menus."""
from pathlib import Path
import runpy

source = runpy.run_path(str(Path(__file__).with_name('install-native-presentation-045-attempt-002.py')))['source']
source = source.replace('native-presentation-045-efi-inventory-attempt-002.json', 'native-presentation-045-efi-archive-017.json')
anchor = '    request = dict(inventory=inventory,'
assert source.count(anchor) == 1
source = source.replace(anchor, "    historical032 = json.loads((base/'reports/native-presentation-044-efi-inventory.json').read_text())['configs']['loader/entries/native-original-graphics-032.conf']\n" + anchor)
anchor = "prepare_entry(inventory['configs']['loader/entries/native-original-graphics-032.conf'])"
assert source.count(anchor) == 1
source = source.replace(anchor, 'prepare_entry(historical032)')
compile(source, 'install045-attempt003', 'exec')
if __name__ == '__main__':
    exec(compile(source, 'install045-attempt003', 'exec'), {'__name__': '__main__', '__file__': __file__})
