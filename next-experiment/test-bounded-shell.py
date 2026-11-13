"""Run against the real, native ARM helper as root on the lab host."""
import subprocess
import sys
import time

binary = sys.argv[1]
def run(command, limit=3):
    return subprocess.run([binary, str(limit), command, '/bin/sh'], text=True, capture_output=True, timeout=limit + 5)

identity = run('id -u; id -g; grep CapEff /proc/self/status')
assert identity.returncode == 0, identity
assert '2000\n2000\n' in identity.stdout, identity.stdout
assert 'CapEff:\t0000000000000000' in identity.stdout, identity.stdout
nonzero = run('exit 7')
assert nonzero.returncode == 7, nonzero
start = time.monotonic()
blocked = run('sleep 20', 1)
assert blocked.returncode == 124, blocked
assert time.monotonic() - start < 5
print('PASS: real UID/GID 2000, no effective capabilities, exit status and bounded timeout')
