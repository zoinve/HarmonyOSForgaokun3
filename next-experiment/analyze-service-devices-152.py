"""Analyze actual service-root nodes, without confusing outer initramfs modes."""
from pathlib import Path
import hashlib
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]


def summarize(text):
    current = None
    samples = []
    for line in text.splitlines():
        start = re.fullmatch(r'SERVICEDEV152_BEGIN stage=(\w+) mono_ms=(\d+) read_only=1 input_events_read=0', line)
        if start:
            current = dict(stage=start[1], mono_ms=int(start[2]), roots=[], nodes=[], missing=[], refused=[], complete=False)
            samples.append(current)
            continue
        if current is None:
            continue
        if line.startswith('SERVICEDEV152_END '):
            current['complete'] = True
            current = None
            continue
        root = re.fullmatch(r'SERVICEDEV152_ROOT stage=\w+ pid=(\d+) service=(\w+) private_tmpfs=1', line)
        if root:
            current['roots'].append(dict(pid=int(root[1]), service=root[2], private_tmpfs=True))
        node = re.fullmatch(r'SERVICEDEV152_NODE stage=\w+ pid=(\d+) service=(\w+) node=(\S+) uid=(\d+) gid=(\d+) mode=([0-7]+) char=([01]) major=(\d+) minor=(\d+) kernel_match=([01])', line)
        if node:
            pid, service, path, uid, gid, mode, char, major, minor, match = node.groups()
            current['nodes'].append(dict(pid=int(pid), service=service, node=path, uid=int(uid), gid=int(gid),
                mode=mode, char=char == '1', major=int(major), minor=int(minor), kernel_match=match == '1'))
        missing = re.fullmatch(r'SERVICEDEV152_NODE_MISSING stage=\w+ pid=(\d+) service=(\w+) node=(\S+) errno=(\d+) expected_major=(\d+) expected_minor=(\d+)', line)
        if missing:
            pid, service, path, error, major, minor = missing.groups()
            current['missing'].append(dict(pid=int(pid), service=service, node=path, errno=int(error), expected_major=int(major), expected_minor=int(minor)))
        refused = re.fullmatch(r'SERVICEDEV152_ROOT_REFUSED stage=\w+ pid=(\d+) service=(\w+) errno=(\d+)', line)
        if refused:
            current['refused'].append(dict(pid=int(refused[1]), service=refused[2], errno=int(refused[3])))
    completed = [sample for sample in samples if sample['complete']]
    latest = completed[-1] if completed else None
    return dict(samples=samples, latest_complete_sample=latest, permissions_changed=False,
        service_usb_nodes_observed=bool(latest and any(row['node'].startswith('/dev/bus/usb/') for row in latest['nodes'])),
        service_usb_nodes_missing=[row for row in latest['missing'] if row['node'].startswith('/dev/bus/usb/')] if latest else [],
        physical_touch_accuracy_verified=False, usb_storage_file_access_verified=False)


if __name__ == '__main__':
    report = ROOT / 'reports/commercial61-native-152'
    output = report / 'service-devices-runtime-analysis-152.json'
    assert not output.exists()
    evidence = report / 'runtime-evidence'
    manifest = json.loads((evidence / 'retrieval-manifest.json').read_text())
    for name, row in manifest['files'].items():
        raw = (evidence / 'raw' / name).read_bytes()
        assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], name
    phase = max((n for n in manifest['files'] if re.fullmatch(r'phase-\d+\.log', n)), key=lambda n: int(n[6:-4]))
    text = (evidence / 'raw' / phase).read_bytes().decode('utf-8', errors='replace')
    data = summarize(text)
    data['input_usb148'] = runpy.run_path(str(ROOT / 'next-experiment/analyze-input-usb-148.py'))['summarize'](text)
    data.update(run=manifest['run'], phase_file=phase, all_evidence_hashes_verified=True, verified_file_count=len(manifest['files']))
    output.open('x').write(json.dumps(data, indent=2))
    latest = data['latest_complete_sample']
    print(json.dumps(dict(run=data['run'], samples=len(data['samples']), phase_file=phase,
        latest=latest, native_mmi_holds_touchscreen=data['input_usb148']['native_mmi_holds_touchscreen'],
        storage_modules_live=data['input_usb148']['storage_modules_live']), indent=2))
