"""Allow only the two observed I2C-derived built-in promotions; preserve failed001."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('build-original-graphics-kernel-001.py')))['payload']
payload = payload.replace('original-graphics-kernel-001', 'original-graphics-kernel-002')
old = "assert all(k.startswith(prefixes) and v['after']!='n' for k,v in changes.items()),changes"
new = """extra={'CONFIG_RTC_I2C_AND_SPI','CONFIG_I3C_OR_I2C'}
 assert all((k.startswith(prefixes) or (k in extra and v==dict(before='m',after='y'))) and v['after']!='n' for k,v in changes.items()),changes"""
assert payload.count(old) == 1
payload = payload.replace(old, new)
compile(payload, 'original-graphics-kernel-002', 'exec')
if __name__ == '__main__':
    result = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=payload, text=True, timeout=7800)
    raise SystemExit(result.returncode)
