"""Require same complete observation for device identity, MMI fd and module state."""
from pathlib import Path
import hashlib
import json
import re
import runpy

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
LEGACY = runpy.run_path(str(BASE / 'analyze-input-usb-148.py'))['summarize']


def summarize(text):
    samples = []
    chunk = None
    incomplete = 0
    for line in text.splitlines():
        start = re.fullmatch(r'INPUTUSB148_OBSERVE_BEGIN stage=(\w+) mono_ms=(\d+) read_only=1 input_events_read=0', line)
        if start:
            if chunk is not None:
                incomplete += 1
            stage, stamp = start.groups()
            chunk = [line]
            continue
        if chunk is None:
            continue
        if line.startswith('INPUTUSB148_OBSERVE_END '):
            expected = 'INPUTUSB148_OBSERVE_END stage='+stage+' physical_interaction_acceptance_not_inferred=1'
            if line == expected:
                sample = LEGACY('\n'.join(chunk + [line]))['samples'][0]
                touch = {node:row for node,row in sample['input'].items()
                         if row.get('name') == 'Himax Capacitive TouchScreen'}
                held = [fd for fd in sample['service_fds']
                        if fd['name'] == 'multimodalinput' and fd['node'] in touch]
                sample['touchscreen_nodes'] = touch
                sample['mmi_touchscreen_fds'] = held
                sample['storage_modules_live_together'] = all(
                    sample['modules'].get(module, {}).get('initstate') == 'live'
                    for module in ['usb_storage','uas','exfat'])
                samples.append(sample)
            else:
                incomplete += 1
            chunk = None
            continue
        line_stage = re.search(r'\bstage=(\w+)', line)
        if not line_stage or line_stage[1] != stage:
            continue
        line_stamp = re.search(r'\bmono_ms=(\d+)', line)
        if line_stamp and line_stamp[1] != stamp:
            continue
        if line.startswith(('GAOKUN_DRIVER133 ', 'INPUTUSB148_')):
            chunk.append(line)
    if chunk is not None:
        incomplete += 1
    return dict(samples=samples,incomplete_or_mismatched_samples=incomplete,
        native_mmi_holds_touchscreen=any(sample['mmi_touchscreen_fds'] for sample in samples),
        storage_modules_live_together=any(sample['storage_modules_live_together'] for sample in samples),
        physical_touch_accuracy_verified=False,physical_multitouch_verified=False,
        physical_usb_hid_hotplug_verified=False,usb_storage_file_access_verified=False)


if __name__ == '__main__':
    report = ROOT / 'reports/input-baseline-179'
    assert not report.exists(), 'preserve numbered evidence'
    evidence = ROOT / 'reports/commercial61-native-173/runtime-evidence'
    manifest = json.loads((evidence / 'retrieval-manifest.json').read_text())
    for name,row in manifest['files'].items():
        raw = (evidence / 'raw' / name).read_bytes()
        assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],name
    phases = [name for name in manifest['files'] if re.fullmatch(r'phase-\d+\.log',name)]
    phase = max(phases,key=lambda name:int(name[6:-4]))
    result = summarize((evidence / 'raw' / phase).read_text(errors='replace'))
    result.update(run=manifest['run'],phase_file=phase,verified_file_count=len(manifest['files']),
                  source_runtime_modified=False,coordinate_transform_changed=False)
    report.mkdir()
    (report / 'result.json').open('x').write(json.dumps(result,indent=2))
    compact = {key:value for key,value in result.items() if key!='samples'}
    compact['samples'] = [dict(monotonic_ms=s['mono_ms'],touchscreen_nodes=s['touchscreen_nodes'],
        mmi_touchscreen_fds=s['mmi_touchscreen_fds']) for s in result['samples']]
    print(json.dumps(compact,indent=2))
