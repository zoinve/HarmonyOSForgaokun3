"""Keep native hardware metadata separate from physical interaction acceptance."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def summarize(text):
    samples = []
    current = None
    results = []
    for line in text.splitlines():
        start = re.fullmatch(r'INPUTUSB148_OBSERVE_BEGIN stage=(\w+) mono_ms=(\d+) read_only=1 input_events_read=0', line)
        if start:
            current = dict(stage=start[1], mono_ms=int(start[2]), input={}, usb={}, modules={},
                           service_fds=[], services=[], usb_nodes=[], missing_usb_nodes=[], completed=False)
            samples.append(current)
            continue
        module = re.fullmatch(r'INPUTUSB148_MODULE_RESULT module=(\w+) status=(\d+) storage_acceptance_not_inferred=1', line)
        if module:
            results.append(dict(module=module[1], status=int(module[2])))
        if current is None:
            continue
        if line.startswith('INPUTUSB148_OBSERVE_END '):
            current['completed'] = line == ('INPUTUSB148_OBSERVE_END stage=' + current['stage'] +
                ' physical_interaction_acceptance_not_inferred=1')
            current = None
            continue
        stage = re.search(r'\bstage=(\w+)', line)
        timestamp = re.search(r'\bmono_ms=(\d+)', line)
        if stage and stage[1] != current['stage']:
            continue
        if timestamp and int(timestamp[1]) != current['mono_ms']:
            continue
        attr = re.fullmatch(r'GAOKUN_DRIVER133 stage=\w+ mono_ms=\d+ path=(\S+) attr=(\S+) valid=1 value=(.*)', line)
        if attr:
            path, name, value = attr.groups()
            event = re.fullmatch(r'/sys/class/input/(event\d+)/device', path)
            if event:
                current['input'].setdefault('/dev/input/' + event[1], {})[name] = value
            elif path.startswith('/sys/bus/usb/devices/'):
                current['usb'].setdefault(path, {})[name] = value
            elif path.startswith('/sys/module/'):
                current['modules'].setdefault(path.rsplit('/', 1)[1], {})[name] = value
        axis = re.fullmatch(r'INPUTUSB148_AXIS stage=\w+ node=(\S+) code=(\d+) min=(-?\d+) max=(-?\d+) fuzz=(-?\d+) flat=(-?\d+) resolution=(-?\d+)', line)
        if axis:
            node, code, low, high, fuzz, flat, resolution = axis.groups()
            current['input'].setdefault(node, {}).setdefault('axes', {})[code] = dict(
                minimum=int(low), maximum=int(high), fuzz=int(fuzz), flat=int(flat), resolution=int(resolution))
        perm = re.fullmatch(r'INPUTUSB148_EVDEV_NODE stage=\w+ node=(\S+) uid=(\d+) gid=(\d+) mode=([0-7]+) major=(\d+) minor=(\d+)', line)
        if perm:
            node, uid, gid, mode, major, minor = perm.groups()
            current['input'].setdefault(node, {})['permissions'] = dict(uid=int(uid), gid=int(gid), mode=mode, major=int(major), minor=int(minor))
        fd = re.fullmatch(r'INPUTUSB148_SERVICE_FD stage=\w+ pid=(\d+) name=(\w+) fd=(\d+) node=(\S+)', line)
        if fd:
            pid, name, number, node = fd.groups()
            current['service_fds'].append(dict(pid=int(pid), name=name, fd=int(number), node=node))
        service = re.fullmatch(r'INPUTUSB148_SERVICE stage=\w+ pid=(\d+) name=(\w+)', line)
        if service:
            current['services'].append(dict(pid=int(service[1]), name=service[2]))
        usb_node = re.fullmatch(r'INPUTUSB148_USB_NODE stage=\w+ node=(\S+) uid=(\d+) gid=(\d+) mode=([0-7]+)', line)
        if usb_node:
            current['usb_nodes'].append(dict(node=usb_node[1], uid=int(usb_node[2]), gid=int(usb_node[3]), mode=usb_node[4]))
        missing = re.fullmatch(r'INPUTUSB148_USB_NODE_MISSING stage=\w+ node=(\S+)', line)
        if missing:
            current['missing_usb_nodes'].append(missing[1])
        binding = re.fullmatch(r'INPUTUSB148_USB_BINDING stage=\w+ path=(\S+) driver=(\S+) errno=(\d+)', line)
        if binding:
            current['usb'].setdefault(binding[1], {}).update(driver=binding[2], driver_errno=int(binding[3]))
    touches = [dict(node=node, **info) for sample in samples for node, info in sample['input'].items()
               if info.get('name') == 'Himax Capacitive TouchScreen']
    complete = [sample for sample in samples if sample['completed']]
    return dict(samples=samples, module_results=results, touchscreen_samples=touches,
                native_mmi_holds_touchscreen=any(fd['name'] == 'multimodalinput' and
                    sample['input'].get(fd['node'], {}).get('name') == 'Himax Capacitive TouchScreen'
                    for sample in complete for fd in sample['service_fds']),
                storage_modules_live=any(all(sample['modules'].get(module, {}).get('initstate') == 'live'
                    for module in ['usb_storage', 'uas', 'exfat']) for sample in complete),
                physical_touch_accuracy_verified=False, physical_usb_hid_verified=False,
                usb_storage_file_access_verified=False)


if __name__ == '__main__':
    report = ROOT / 'reports/commercial61-native-148'
    output = report / 'input-usb-runtime-analysis-148.json'
    assert not output.exists()
    evidence = report / 'runtime-evidence'
    manifest = json.loads((evidence / 'retrieval-manifest.json').read_text())
    for name, row in manifest['files'].items():
        raw = (evidence / 'raw' / name).read_bytes()
        assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], name
    phase = max((n for n in manifest['files'] if re.fullmatch(r'phase-\d+\.log', n)), key=lambda n: int(n[6:-4]))
    text = (evidence / 'raw' / phase).read_bytes().decode('utf-8', errors='replace')
    data = summarize(text)
    data.update(run=manifest['run'], phase_file=phase, all_evidence_hashes_verified=True,
                verified_file_count=len(manifest['files']))
    output.open('x').write(json.dumps(data, indent=2))
    print(json.dumps(dict(run=data['run'], phase_file=phase, samples=len(data['samples']),
        touchscreen_samples=data['touchscreen_samples'][-1:], native_mmi_holds_touchscreen=data['native_mmi_holds_touchscreen'],
        module_results=data['module_results'], storage_modules_live=data['storage_modules_live'],
        service_fds=data['samples'][-1]['service_fds'] if data['samples'] else [],
        usb_nodes=data['samples'][-1]['usb_nodes'] if data['samples'] else []), indent=2))
