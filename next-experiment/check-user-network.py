"""Configuration-only check: opt-in outbound NAT, no inbound port forwards."""
from pathlib import Path
import sys

path = Path(__file__).with_name('run.py').resolve()
number = next(n for n in range(9915, 99999) if not path.with_name(f'run-{n}').exists())
for enabled in (False, True):
    sys.argv = [str(path), str(number), '--virgl', '--relative-mouse']
    if enabled:
        sys.argv.append('--user-network')
    scope = {'__file__': str(path)}
    text = path.read_text()
    exec(compile(text[:text.index("subprocess.run(['ssh', 'matebook', 'mkdir '")], str(path), 'exec'), scope)
    command = scope['c']['command']
    if enabled:
        assert '-nic' not in command
        assert command[command.index('-netdev') + 1] == 'user,id=normalnet'
        assert 'virtio-net-device,netdev=normalnet' in command
        assert not any('hostfwd' in s or 'guestfwd' in s for s in command)
    else:
        assert command[command.index('-nic') + 1] == 'none'
    assert command[command.index('-accel') + 1] == 'kvm'
    assert scope['c']['qmp_screenshots_enabled'] is False
print('PASS: opt-in normal NAT without port forwards; default isolated and KVM preserved')
