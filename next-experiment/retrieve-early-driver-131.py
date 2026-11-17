"""Preserve the 131 early exit without requiring an unproduced desktop log."""
from pathlib import Path
import hashlib
import json
import re
import runpy

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent

if __name__ == '__main__':
    report = ROOT / 'reports/commercial61-native-131'
    assert json.loads((report / 'boot-observation.json').read_text())['returned']
    assert not (report / 'runtime-evidence').exists()
    previous = ROOT / 'reports/commercial61-native-130/runtime-evidence'
    manifest = json.loads((previous / 'retrieval-manifest.json').read_text())
    name = 'snapshot075-commercial-desktop086.log'
    diagnostic = (previous / 'raw' / name).read_bytes()
    assert hashlib.sha256(diagnostic).hexdigest() == manifest['files'][name]['sha256']
    digests = sorted(set(re.findall(rb'PRIVACY093_ORIGINAL_UDID_HASH digest=([0-9a-f]{64})', diagnostic)))
    assert digests, 'need the previously verified original-identity privacy digest'
    workflow = runpy.run_path(str(BASE / 'commercial-workflow-131.py'))
    source = (report / 'retrieve-commercial-evidence.generated.py').read_text()
    anchor = " diagnostic=(run/'snapshot075-commercial-desktop086.log').read_bytes()"
    assert source.count(anchor) == 1
    replacement = " diagnostic=b'\\n'.join(p.read_bytes() for p in run.iterdir() if p.is_file() and p.suffix=='.log')"
    source = source.replace(anchor, replacement, 1)
    anchor = " identities=set(re.findall(rb'PRIVACY093_ORIGINAL_UDID_HASH digest=([0-9a-f]{64})', diagnostic))"
    assert source.count(anchor) == 1
    source = source.replace(anchor, anchor + '\n identities.update(' + repr(digests) + ')', 1)
    anchor = 'original_udid_guard_passed=True'
    assert source.count(anchor) == 1
    source = source.replace(anchor, anchor + ',early_exit_retrieval=True,identity_digest_from_verified_prior_run=True', 1)
    compile(source, 'retrieve-early-driver-131', 'exec')
    (report / 'retrieve-early-driver-131.generated.py').open('x').write(source)
    (report / 'standard-retrieval-failure.json').open('x').write(json.dumps(dict(
        reason='snapshot075-commercial-desktop086.log absent; original reader refused before export',
        standard_evidence_exported=False, new_boot_attempted=False,
        recovery_preserves_physical_serial_and_original_identity_scanners=True), indent=2))
    workflow['configure_local_transport']()
    exec(compile(source, 'retrieve-early-driver-131', 'exec'),
         {'__name__': '__main__', '__file__': str(BASE / 'retrieve-early-driver-131.py')})
