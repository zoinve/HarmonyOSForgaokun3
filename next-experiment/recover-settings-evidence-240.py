"""Record late Ubuntu return and recover235 without rewriting the timeout."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import runpy
import subprocess

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REPORT = ROOT / 'reports/commercial61-native-235'

if __name__ == '__main__':
    workflow = runpy.run_path(str(BASE / 'commercial-workflow-235.py'))
    workflow['configure_local_transport']()
    late = REPORT / 'late-return-observation-240.json'
    assert not late.exists()
    query = "from pathlib import Path;import json,subprocess;print(json.dumps(dict(boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),release=subprocess.check_output(['uname','-r'],text=True).strip())))"
    command = ['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes', '-o', 'HostName=192.168.10.128', '-o', 'HostKeyAlias=192.168.10.128', 'matebook', 'python3 -']
    state = json.loads(subprocess.check_output(command, input=query, text=True, timeout=30))
    original = json.loads((REPORT / 'boot-observation.json').read_text())
    assert state['release'] == '7.1.0-rc3-gaokun3+'
    assert state['boot_id'] != original['before_boot_id']
    late.open('x').write(json.dumps(dict(returned=True, ubuntu=state, observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), original_observation_returned=original['returned'], automatic_return_cause_verified=False, new_boot_requested=False), indent=2))
    source = (REPORT / 'verify-commercial-return.generated.py').read_text()
    assert source.count("root/'boot-observation.json'") == 1
    source = source.replace("root/'boot-observation.json'", "root/'late-return-observation-240.json'")
    try:
        exec(compile(source, 'late-preservation-240', 'exec'), {'__name__': '__main__', '__file__': str(BASE / 'late-preservation-240.py')})
    except Exception as error:
        (REPORT / 'late-preservation-failure-240.json').open('x').write(json.dumps(dict(error=str(error), preservation_verified=False), indent=2))
    assert not (REPORT / 'runtime-evidence').exists()
    previous = ROOT / 'reports/commercial61-native-201/runtime-evidence'
    manifest = json.loads((previous / 'retrieval-manifest.json').read_text())
    name = 'snapshot075-commercial-desktop086.log'
    open_log = runpy.run_path(str(BASE / 'compress-historical-logs-226.py'))['open_log']
    with open_log(previous / 'raw' / name) as stream:
        diagnostic = stream.read()
    assert hashlib.sha256(diagnostic).hexdigest() == manifest['files'][name]['sha256']
    digests = sorted(set(re.findall(rb'PRIVACY093_ORIGINAL_UDID_HASH digest=([0-9a-f]{64})', diagnostic)))
    assert digests
    source = (REPORT / 'retrieve-commercial-evidence.generated.py').read_text()
    old = " diagnostic=(run/'snapshot075-commercial-desktop086.log').read_bytes()"
    assert source.count(old) == 1
    source = source.replace(old, " diagnostic=b'\\n'.join(p.read_bytes() for p in run.iterdir() if p.is_file() and p.suffix=='.log')")
    old = " identities=set(re.findall(rb'PRIVACY093_ORIGINAL_UDID_HASH digest=([0-9a-f]{64})', diagnostic))"
    assert source.count(old) == 1
    source = source.replace(old, old + '\n identities.update(' + repr(digests) + ')')
    old = 'original_udid_guard_passed=True'
    assert source.count(old) == 1
    source = source.replace(old, old + ',partial_retrieval=True,identity_digest_from_verified_prior_run=True')
    (REPORT / 'partial-retrieval-240.generated.py').open('x').write(source)
    exec(compile(source, 'partial-retrieval-240', 'exec'), {'__name__': '__main__', '__file__': str(BASE / 'partial-retrieval-240.py')})
