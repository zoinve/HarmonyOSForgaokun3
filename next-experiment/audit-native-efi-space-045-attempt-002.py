"""Fresh read-only inventory at the new address; preserve disabled auto-off."""
from pathlib import Path
import runpy

p = runpy.run_path(str(Path(__file__).with_name('native-presentation-session-045.py')))
source = runpy.run_path(str(Path(__file__).with_name('audit-native-efi-space-045.py')))['source']
source = source.replace('native-presentation-045-efi-inventory.json', 'native-presentation-045-efi-inventory-attempt-002.json')
source = source.replace("if __name__ == '__main__':", "REMOTE = _SESSION['timer_guard'](REMOTE)\n\nif __name__ == '__main__':")
source = source.replace('    r.check_returncode()', "    if r.returncode: raise RuntimeError(r.stderr)")
source = p['connection_source'](source)
if __name__ == '__main__':
    exec(compile(source, 'inventory045-attempt002', 'exec'), {'__name__': '__main__', '__file__': __file__})
