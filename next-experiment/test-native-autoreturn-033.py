"""Unattended candidate must not inherit the manual indefinite wait."""
from pathlib import Path
import runpy
base=Path(__file__).resolve().parent
assert (base/'build-native-original-graphics-boot-033.py').is_file(),'missing automatic return candidate'
p=runpy.run_path(str(base/'build-native-original-graphics-boot-033.py'))
o=p['outer']
assert 'left033=420' in o and 'while(left033)left033=sleep(left033)' in o and 'reboot(RB_AUTOBOOT)' in o
assert o.index('pid_t deadline033=fork()') < o.index('char *pcie_phy[]')
assert 'elapsed033<240' in o and 'kill(child,SIGKILL)' in o
assert 'waitpid(child,&state,0)' not in o
assert 'manual_power_cycle_required=1' not in o
assert 'native-interactive-033-%s' in o
assert p['inner']==p['p']['inner']
print('PASS unattended 240-second target window, independent 420-second reboot fallback, 032 userspace retained')
