"""Validate new diagnostic coverage and inherited isolation, without booting."""
from pathlib import Path
import runpy
import subprocess

base = Path(__file__).resolve().parent
builder = base/'build-native-original-graphics-boot-002.py'
assert builder.is_file(), 'missing candidate 002 diagnostic builder'
d = runpy.run_path(str(builder))
inner, outer = d['inner'], d['outer']
assert 'NATIVE_DIAG002_FILE' in inner and 'NATIVE_DIAG002_STAT' in inner
assert 'NATIVE_DIAG002_PROCESS' in inner and 'pid <= 0' in inner
for path in ['/proc/1/mountinfo', '/proc/1/status', '/proc/1/wchan', '/data', '/system/etc/init.cfg']:
    assert '"'+path+'"' in inner
assert 'NATIVE_DIAG002_HOST_PROCESS' in outer
assert 'printk_devkmsg' in outer and 'native_diagnostics(child)' in outer
assert 'CLONE_NEWPID|CLONE_NEWNS|CLONE_NEWNET|SIGCHLD' in outer
assert 'sleep(180); reboot(RB_AUTOBOOT)' in outer
assert 'LO_FLAGS_READ_ONLY|LO_FLAGS_AUTOCLEAR' in outer
assert 'platform_libcxx_replaced=0' in inner
print('PASS: namespace/init/data diagnostics and inherited safety gates')
if __name__ == '__main__':
    payload = runpy.run_path(str(base/'test-native-original-graphics-boot-001.py'))['payload']
    payload = payload.replace('native-original-graphics-boot-001', 'native-original-graphics-boot-002')
    raise SystemExit(subprocess.run(['wsl','-d','Debian','--','python3','-'],input=payload,text=True).returncode)
