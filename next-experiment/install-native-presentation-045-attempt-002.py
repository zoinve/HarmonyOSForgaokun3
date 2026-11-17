"""Fresh 045 entry only; preserve user-disabled timer and 64 MiB EFI reserve."""
from pathlib import Path
import runpy

p = runpy.run_path(str(Path(__file__).with_name('native-presentation-session-045.py')))
source = runpy.run_path(str(Path(__file__).with_name('install-native-presentation-045.py')))['source']
source = source.replace('native-presentation-045-efi-inventory.json', 'native-presentation-045-efi-inventory-attempt-002.json')
anchor = "REMOTE = head + r'''"
assert source.count(anchor) == 1
source = source.replace(anchor, "head = _SESSION['timer_guard'](head)\n" + anchor)
source = source.replace('ubuntu_default_unchanged=True,',
                        'ubuntu_default_unchanged=True,screenoff_timer_inactive_disabled_preserved=True,')
source = p['connection_source'](source)
if __name__ == '__main__':
    exec(compile(source, 'install045-attempt002', 'exec'), {'__name__': '__main__', '__file__': __file__})
