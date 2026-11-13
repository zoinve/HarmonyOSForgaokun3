"""One fresh mount-corrected diagnostic boot; keep immediate bounded reconnect."""
from pathlib import Path

source = Path(__file__).with_name('run-native-presentation-043.py').read_text()
for old, new in [('native-original-graphics-boot-043', 'native-original-graphics-boot-044'),
                 ('native-original-graphics-043', 'native-original-graphics-044'),
                 ('native-presentation-043-installation.json', 'native-presentation-044-installation.json'),
                 ('NATIVE043_REBOOT_REQUESTED', 'NATIVE044_REBOOT_REQUESTED')]:
    assert old in source, old
    source = source.replace(old, new)
compile(source, 'single-native044-boot', 'exec')
scope = {'__name__': __name__, '__file__': __file__}
exec(compile(source, 'single-native044-boot', 'exec'), scope)
observe_return = scope['observe_return']
PREPARE = scope['PREPARE']
REBOOT = scope['REBOOT']
CANCEL_OWN_SELECTION = scope['CANCEL_OWN_SELECTION']
