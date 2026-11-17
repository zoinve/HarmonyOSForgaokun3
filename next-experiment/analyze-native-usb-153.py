"""Correlate original libusb enumeration with real kernel device metadata."""
from pathlib import Path
import hashlib
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]


def summarize(text):
    init = [int(value) for value in re.findall(r'^USB153_INIT status=(-?\d+) backend_only=1$', text, re.M)]
    counts = [int(value) for value in re.findall(r'^USB153_LIST count=(-?\d+) backend_only=1 service_acceptance_not_inferred=1$', text, re.M)]
    ends = [int(value) for value in re.findall(r'^USB153_END status=(\d+) configuration_changed=0 interfaces_claimed=0 serials_read=0$', text, re.M)]
    probes = [int(value) for value in re.findall(r'^USB153_PROBE_RESULT status=(\d+) backend_only=1$', text, re.M)]
    devices = [dict(bus=int(bus), address=int(address), node=node) for bus, address, node in re.findall(
        r'^USB153_DEVICE bus=(\d+) address=(\d+) node=(/dev/bus/usb/\d+/\d+)$', text, re.M)]
    valid_nodes = all(row['node'] == '/dev/bus/usb/%03d/%03d' % (row['bus'], row['address']) for row in devices)
    success = init == [0] and len(counts) == 1 and 0 <= counts[0] <= 128 and ends == [0] and probes == [0]
    success = success and valid_nodes and counts[0] == len(devices) and len({row['node'] for row in devices}) == len(devices)
    return dict(init_results=init, list_counts=counts, end_results=ends, probe_results=probes, devices=devices,
        refusals=re.findall(r'^USB153_REFUSED reason=(\w+)$', text, re.M),
        original_backend_enumeration_completed=success, usb_service_acceptance_verified=False,
        physical_usb_hid_verified=False, usb_storage_file_access_verified=False)


if __name__ == '__main__':
    report = ROOT / 'reports/commercial61-native-153'
    output = report / 'native-usb-runtime-analysis-153.json'
    assert not output.exists()
    evidence = report / 'runtime-evidence'
    manifest = json.loads((evidence / 'retrieval-manifest.json').read_text())
    for name, row in manifest['files'].items():
        raw = (evidence / 'raw' / name).read_bytes()
        assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], name
    phase = max((n for n in manifest['files'] if re.fullmatch(r'phase-\d+\.log', n)), key=lambda n: int(n[6:-4]))
    phase_text = (evidence / 'raw' / phase).read_bytes().decode('utf-8', errors='replace')
    backend_name = 'snapshot075-commercial-desktop086.log'
    data = summarize((evidence / 'raw' / backend_name).read_bytes().decode('utf-8', errors='replace'))
    input_data = runpy.run_path(str(ROOT / 'next-experiment/analyze-input-usb-148.py'))['summarize'](phase_text)
    namespace_data = runpy.run_path(str(ROOT / 'next-experiment/analyze-service-devices-152.py'))['summarize'](phase_text)
    latest = next((row for row in reversed(input_data['samples']) if row['completed']), None)
    observed = {row['node'] for row in data['devices']}
    kernel_devices = []
    for path, row in (latest['usb'].items() if latest else []):
        if not all(key in row for key in ['idVendor', 'idProduct', 'busnum', 'devnum']):
            continue
        node = '/dev/bus/usb/%03d/%03d' % (int(row['busnum']), int(row['devnum']))
        kernel_devices.append(dict(path=path, node=node, vendor=row['idVendor'], product=row['idProduct'],
            device_class=row.get('bDeviceClass'), original_backend_observed=node in observed))
    data.update(run=manifest['run'], phase_file=phase, backend_file=backend_name,
        all_evidence_hashes_verified=True, verified_file_count=len(manifest['files']),
        kernel_comparison_sample_mono_ms=latest['mono_ms'] if latest else None, kernel_devices=kernel_devices,
        native_mmi_holds_touchscreen=input_data['native_mmi_holds_touchscreen'], storage_modules_live=input_data['storage_modules_live'],
        service_namespace_analysis=namespace_data)
    output.open('x').write(json.dumps(data, indent=2))
    print(json.dumps({key: data[key] for key in ['run', 'verified_file_count', 'init_results', 'list_counts', 'probe_results',
        'original_backend_enumeration_completed', 'refusals', 'kernel_devices', 'native_mmi_holds_touchscreen', 'storage_modules_live']}, indent=2))
