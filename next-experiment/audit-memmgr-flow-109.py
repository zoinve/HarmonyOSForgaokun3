"""Seal original initialization branches; do not infer runtime branch outcomes."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/memmgr-initialization-audit-109'
LIBRARY = OUT / 'libmemmgrservice.z.so'


if __name__ == '__main__':
    assert hashlib.sha256(LIBRARY.read_bytes()).hexdigest() == '2cf2566bb7bf580513e82c6d1819775886cfe3ecd35a5e2b14a0eae60dceb012'
    destination = OUT / 'flow-analysis.json'
    assert not destination.exists()
    ranges = {'service-start': (0x19b040, 0x19b4ec),
              'service-init': (0x19e64c, 0x19e9a0),
              'strategy-init': (0x1d7124, 0x1d7520),
              'root-memcg-parameters': (0x1d34c4, 0x1d3740)}
    hashes = {}
    for name, (start, end) in ranges.items():
        data = subprocess.check_output(['aarch64-linux-gnu-objdump', '-d', '-C',
            '--start-address=' + hex(start), '--stop-address=' + hex(end), str(LIBRARY)])
        (OUT / (name + '.disassembly.txt')).open('xb').write(data)
        hashes[name] = hashlib.sha256(data).hexdigest()
    result = dict(library_sha256=hashlib.sha256(LIBRARY.read_bytes()).hexdigest(),
        disassembly_sha256=hashes,
        static_branches=[
            dict(site='0x19b100', action='call MemMgrService::Init'),
            dict(site='0x19b104', action='branch to 0x19b298 on false; skips Publish'),
            dict(site='0x19b12c', action='call SystemAbility::Publish after successful Init'),
            dict(site='0x19b150', action='branch to 0x19b2f0 on Publish failure'),
            dict(site='0x19e690', action='branch on ReclaimPriorityManager::Init failure'),
            dict(site='0x19e69c', action='branch on ReclaimStrategyManager::Init failure'),
            dict(site='0x1d71d0', action='call MemcgMgr::SetRootMemcgPara'),
            dict(site='0x1d71d4', action='branch on root memcg parameter setup failure'),
            dict(site='0x1d3540', action='root memcg pointer must be non-null'),
            dict(site='0x1d3548', action='root memcg field at offset 56 must be non-null')],
        runtime_branch_outcome_proven=False,
        access_token_failure_causal_link_proven=False,
        missing_kernel_node_causal_link_proven=False,
        diagnostic_next='Observe original memory service threads and its actual namespace mounts; retain all original checks.',
        target_boot_performed=False, original_binary_modified=False)
    destination.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
