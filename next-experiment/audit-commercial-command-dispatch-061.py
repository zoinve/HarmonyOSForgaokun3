"""Check the original command templates really call the observed handlers."""
from pathlib import Path
import hashlib
import json
import subprocess

BASE = Path(__file__).resolve().parents[1]
CHECKS = [
    ('attach_uni_surface', '0x462a68', '0x462a78', '462a74:', '0x481678'),
    ('add_child', '0x309ca8', '0x309cbc', '309cb8:', '0x309cbc'),
    ('update_recording', '0x44f09c', '0x44f0b0', '44f0ac:', '0x44b678'),
    ('update_modifier_drawcmd', '0x4613cc', '0x4613e0', '4613dc:', '0x47d4fc'),
]


def main():
    out = BASE / 'reports/commercial-command-dispatch-061'
    assert not out.exists(), 'Preserve numbered evidence'
    binary = BASE / 'reports/commercial-oneway-audit-045/base.so'
    sha = hashlib.sha256(binary.read_bytes()).hexdigest()
    assert sha == '40bd0307b161f0f46ea82d3b08e3dca7819a5c4492066f0e462b8e172e2c50c8'
    specs = json.loads((BASE / 'reports/commercial-render-audit-061/result.json').read_text())['probes']
    assembly = {}
    for event, start, end, site, target in CHECKS:
        assert next(r['virtual_address'] for r in specs if r['event'] == event) == target
        text = subprocess.check_output(['llvm-objdump-19', '-d', '--demangle',
            '--start-address=' + start, '--stop-address=' + end, str(binary)], text=True)
        branch = next(line for line in text.splitlines() if site in line)
        assert target in branch and ('\tbl\t' in branch or '\tb\t' in branch), branch
        assembly[event] = text
    out.mkdir()
    for event, text in assembly.items():
        (out / (event + '.asm')).open('x').write(text)
    result = dict(original_base_sha256=sha, command_template_dispatch_verified=True,
        checks=[dict(event=e, start=s, end=n, callsite=c, target=t) for e,s,n,c,t in CHECKS],
        private_object_memory_read=False, security_checks_modified=False,
        runtime_observation_not_claimed=True, actual_desktop_verified=False)
    (out / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
