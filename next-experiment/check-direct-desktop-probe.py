"""Bounded normal-command experiment; no token or activation-state mutation."""
from pathlib import Path
import runpy
base=Path(__file__).resolve().parent
transform=runpy.run_path(str(base/'direct-desktop-probe.py'))['direct_probe']
source=(base/'payload-913/init.c').read_text()
result=transform(source,(base/'bounded-shell.c').read_text())
assert source.count('    gpu913_observe();')==1
assert 'setresuid(0,0,0)' in result
assert 'struct __user_cap_data_struct caps[2] = {{0}};' in result
assert 'setresuid(2000,2000,2000)' in (base/'bounded-shell.c').read_text()
assert 'aa force-stop com.huawei.hmos.hwstartupguide' in result
assert 'kill(' not in result[result.index('static int guide_count916'):result.index('static void command_probe')]
assert 'skip_root_if_guide_absent' in result
assert source[:source.index('static void command_probe')] in result
assert result[result.index('int main(void) {'):]==source[source.index('int main(void) {'):]
print('PASS: bounded normal aa requests, cleared capabilities, unchanged boot/security/graphics')
