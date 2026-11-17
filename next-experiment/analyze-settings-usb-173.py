"""Recheck Settings and sanitized USB identities in hash-verified native evidence."""
from pathlib import Path
import hashlib
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/commercial61-native-173'


def usb_samples(text):
    samples = {}
    pattern = (r'GAOKUN_DRIVER133 stage=(\w+) mono_ms=(\d+) '
               r'path=/sys/bus/usb/devices/([^ ]+) '
               r'attr=(idVendor|idProduct) valid=1 value=([0-9a-fA-F]{4})')
    for stage, milliseconds, device, attribute, value in re.findall(pattern, text):
        samples.setdefault((stage, int(milliseconds)), {}).setdefault(device, {})[attribute] = value.lower()
    return [dict(stage=stage, monotonic_ms=milliseconds,
                 devices=[dict(path=device, vid=attrs['idVendor'], pid=attrs['idProduct'])
                          for device, attrs in sorted(devices.items())
                          if 'idVendor' in attrs and 'idProduct' in attrs])
            for (stage, milliseconds), devices in samples.items()]


if __name__ == '__main__':
    output = REPORT / 'settings-usb-analysis.json'
    assert not output.exists(), 'immutable analysis already exists'
    evidence = REPORT / 'runtime-evidence'
    manifest = json.loads((evidence / 'retrieval-manifest.json').read_text())
    for name, expected in manifest['files'].items():
        data = (evidence / 'raw' / name).read_bytes()
        assert len(data) == expected['bytes']
        assert hashlib.sha256(data).hexdigest() == expected['sha256'], name
    summarize = runpy.run_path(str(ROOT / 'next-experiment/analyze-settings-155.py'))['summarize']
    settings = summarize((evidence / 'raw/interactive-hilog030.log').read_text(errors='replace'))
    live = json.loads((REPORT / 'live-client-observation.json').read_text())
    phase = (evidence / 'raw/phase-172.log').read_text(errors='replace')
    samples = usb_samples(phase)
    baseline = {('1d6b', '0002'), ('1d6b', '0003'), ('12d1', '10b8'), ('0bda', '8153')}
    extra = sorted({(d['vid'], d['pid']) for s in samples for d in s['devices']} - baseline)
    result = dict(run=manifest['run'], verified_file_count=len(manifest['files']),
                  settings=settings,
                  live_settings_bundle_absent_user100='settings_bundle_absent_user100' in
                  live['settings_follow']['stdout'],
                  usb_samples=samples, usb_ids_outside_previous_baseline=extra,
                  usb_serials_exported=False, usb_service_acceptance_verified=False,
                  continuous_usb_hotplug_capture_verified=False,
                  settings_repaired=False, original_packages_modified=False,
                  signature_checks_changed=False)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(dict(settings_launch_failures=settings['correlated_missing_bundle_launch_count'],
                         live_bundle_absent=result['live_settings_bundle_absent_user100'],
                         usb_samples=len(samples), extra_usb_ids=extra,
                         settings_repaired=False), indent=2))
