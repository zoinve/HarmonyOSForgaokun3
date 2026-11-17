"""Constrain passive tracing to the original target and preserve boot protections."""
from pathlib import Path
import hashlib
import json
import runpy

b = Path(__file__).resolve().parent
old = runpy.run_path(str(b / 'build-commercial-native-045.py'))
new = runpy.run_path(str(b / 'build-commercial-native-046.py'))
helper = runpy.run_path(str(b / 'commercial-trace-046.py'))
assert new['inner'] == old['inner']
before = old['outer'].replace('commercial61-native-045', 'commercial61-native-046').replace('COMMERCIAL045', 'COMMERCIAL046')
assert new['outer'] == helper['instrument'](before)
for token in ['elapsed033<150', 'left033=270', 'target_budget_seconds=150',
              'strcmp(expected,actual)', 'instruction!=s->instruction',
              'original_service_continues=1', 'truncated_streams_do_not_prove_absence=1']:
    assert token in new['outer'], token
for token in ['ptrace(', 'process_vm_writev', 'kprobe_override', 'setuid(', 'setgid(']:
    assert token not in helper['HELPER'], token
audit = json.loads((b.parent / 'reports/commercial-trace-audit-046/result.json').read_text())
assert len(audit['probes']) == 14
assert audit['executable_offsets_verified'] and not audit['private_object_memory_read']
assert len({p['event'] for p in audit['probes']}) == len(audit['probes'])
for p in audit['probes']:
    assert int(p['file_offset'], 16) % 4 == 0
    assert len(bytes.fromhex(p['original_instruction'])) == 4
    assert '{root}/system/lib64/' in p['definition']
    assert '+0(' not in p['definition']
for name in ['bootstrap', 'bootstrap.c']:
    previous = b.parent / 'reports/commercial61-native-045' / name
    current = b.parent / 'reports/commercial61-native-046' / name
    if previous.exists() and current.exists():
        assert hashlib.sha256(previous.read_bytes()).digest() == hashlib.sha256(current.read_bytes()).digest()
print('PASS: original userland and bounds unchanged; namespace and exact-instruction guard; 14 real ELF methods; no private objects or service override')
