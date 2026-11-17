"""Correlate real Binder handle/node ownership in a single original sample."""
from pathlib import Path
import hashlib
import json
import re

root = Path(__file__).resolve().parents[1] / 'reports/commercial61-native-044'
evidence = root / 'runtime-evidence'
manifest = json.loads((evidence / 'retrieval-manifest.json').read_text())
phases = sorted(name for name in manifest['files'] if re.fullmatch(r'phase-\d+\.log', name))
path = evidence / 'raw' / phases[-1]
data = path.read_bytes()
assert hashlib.sha256(data).hexdigest() == manifest['files'][path.name]['sha256']
text = data.decode(errors='replace')
header = re.compile(r'^COMMERCIAL044_OUTER_PROCESS global_pid=(\d+) target=(\d+) namespace=(\S+) mono_sec=(\d+) command=([^\n]+)\n', re.MULTILINE)
matches = list(header.finditer(text))
observations = []
stream = re.compile(r'^COMMERCIAL044_OUTER_STREAM_BEGIN path=(\S+) limit=(\d+)\n(.*?)'
                    r'^COMMERCIAL044_OUTER_STREAM_END path=(\S+) bytes=(\d+) eof=(\d+) errno=(\d+)$', re.MULTILINE | re.DOTALL)
for index, match in enumerate(matches):
    body = text[match.end():matches[index + 1].start() if index + 1 < len(matches) else len(text)]
    parts = []
    for part in stream.finditer(body):
        assert part[1] == part[4]
        parts.append(dict(path=part[1], bytes=int(part[5]), eof=int(part[6]), errno=int(part[7]), body=part[3]))
    status = next((p['body'] for p in parts if p['path'].endswith('/status')), '')
    namespaces = re.search(r'^NSpid:\s+([^\n]+)', status, re.MULTILINE)
    ids = [int(n) for n in namespaces[1].split()] if namespaces else []
    if ids:
        assert ids[0] == int(match[1])
    binder = next((p for p in parts if '/binder/proc/' in p['path']), None)
    refs, nodes = [], []
    if binder:
        refs = [dict(ref=int(m[1]), handle=int(m[2]), node=int(m[4]), dead=bool(m[3]))
                for m in re.finditer(r'^  ref (\d+): desc (\d+) (dead )?node (\d+)', binder['body'], re.MULTILINE)]
        nodes = [int(m[1]) for m in re.finditer(r'^  node (\d+):', binder['body'], re.MULTILINE)]
    observations.append(dict(global_pid=int(match[1]), target=int(match[2]), namespace=match[3],
                             mono_sec=int(match[4]), command=match[5], nspid=ids,
                             inner_pid=ids[-1] if len(ids) > 1 else None, refs=refs, nodes=nodes,
                             streams=parts))
ipc = json.loads((root / 'binder-analysis.json').read_text())
links = []
for record in ipc['records']:
    if record['phase'] != 'return' or record['interface'] != 3:
        continue
    for caller in observations:
        if caller['inner_pid'] != record['pid']:
            continue
        reference = next((r for r in caller['refs'] if r['handle'] == record['handle'] and not r['dead']), None)
        if not reference:
            continue
        for owner in observations:
            if owner['mono_sec'] != caller['mono_sec'] or owner['namespace'] != caller['namespace']:
                continue
            if reference['node'] in owner['nodes']:
                links.append(dict(caller_inner=record['pid'], caller_global=caller['global_pid'],
                                  code=record['code'], serial=record['serial'],
                                  handle=record['handle'], node=reference['node'],
                                  owner_inner=owner['inner_pid'], owner_global=owner['global_pid'],
                                  owner_command=owner['command'], sample_sec=caller['mono_sec'],
                                  ioctl_success=record['result'] == 0,
                                  kernel_consumed=record['consumed'] >= record['end'],
                                  same_sample_endpoint_ownership_not_execution=True))
result = dict(phase=path.name, phase_sha256=hashlib.sha256(data).hexdigest(),
              observations=observations, endpoint_links=links,
              actual_desktop_verified=False, service_execution_not_inferred=True)
with (root / 'endpoint-analysis.json').open('x') as out:
    json.dump(result, out, indent=2)
print(json.dumps(dict(observations=len(observations),
                      binder_errors=[dict(pid=o['global_pid'], errno=s['errno'], eof=s['eof'], bytes=s['bytes'])
                                     for o in observations for s in o['streams'] if '/binder/proc/' in s['path']],
                      links=len(links), linked_codes=sorted({l['code'] for l in links}),
                      actual_desktop_verified=False), indent=2))
