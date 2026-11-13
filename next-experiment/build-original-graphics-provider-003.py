"""Trace a copy of the full reference provider; preserve failed/earlier builds."""
from pathlib import Path
import runpy
import subprocess

payload = runpy.run_path(str(Path(__file__).with_name('build-original-graphics-provider-002.py')))['payload']
payload = payload.replace('original-graphics-provider-002', 'original-graphics-provider-003')
anchor = "commands=["
assert payload.count(anchor) == 1
payload = payload.replace(anchor, '''trace=runpy.run_path(str(project/'next-experiment/original-composer-trace-001.py'))
original=(ref/'composer.cpp').read_text()
traced=trace['adapt'](original)
assert trace['strip_trace'](traced)==original
composer=work/'composer-traced.cpp'
composer.write_text(traced)
includes.append('-I'+str(ref))
commands=[''')
anchor = "*includes,str(ref/'composer.cpp'),"
assert payload.count(anchor) == 1
payload = payload.replace(anchor, "*includes,str(composer),")
payload = payload.replace("runtime_executed=False,", "runtime_executed=False, bounded_composer_trace=True, original_operations_unchanged=True,")
compile(payload, 'original-graphics-provider-003', 'exec')
if __name__ == '__main__':
    result = subprocess.run(['wsl', '-d', 'Debian', '--', 'python3', '-'], input=payload,
                            text=True, timeout=240)
    raise SystemExit(result.returncode)
