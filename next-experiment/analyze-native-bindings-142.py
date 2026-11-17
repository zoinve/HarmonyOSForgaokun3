"""Preserve verified per-run media observations, including failed diagnostics."""
from pathlib import Path
import hashlib
import json
import re
import runpy
import sys

ROOT = Path(__file__).resolve().parents[1]


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ['139', '141', '145', '148', '152', '153']
    report = ROOT / ('reports/commercial61-native-' + sys.argv[1])
    output = report / 'binding-runtime-analysis-142.json'
    assert not output.exists()
    evidence = report / 'runtime-evidence'
    manifest = json.loads((evidence / 'retrieval-manifest.json').read_text())
    for name, row in manifest['files'].items():
        raw = (evidence / 'raw' / name).read_bytes()
        assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], name
    phase = max((n for n in manifest['files'] if re.fullmatch(r'phase-\d+\.log', n)), key=lambda n: int(n[6:-4]))
    text = (evidence / 'raw' / phase).read_bytes().decode('utf-8', errors='replace')
    media = runpy.run_path(str(ROOT / 'next-experiment/analyze-native-media-138.py'))['summarize'](text)
    baseline = runpy.run_path(str(ROOT / 'next-experiment/analyze-native-drivers-133.py'))['summarize']
    driver = baseline(text, (evidence / 'raw/interactive-hilog030.log').read_bytes().decode('utf-8', errors='replace'))
    bindings = [dict(stage=s, path=p, driver=d, errno=int(e)) for s, p, d, e in re.findall(
        r'^MEDIA139_BINDING stage=(\w+) path=(\S+) driver=(\S+) errno=(\d+)$', text, re.M)]
    media.update(run=manifest['run'], phase_file=phase, phase_sha256=manifest['files'][phase]['sha256'],
                 all_evidence_hashes_verified=True, verified_file_count=len(manifest['files']),
                 bindings=bindings,
                 deferred_probe_samples=[r for r in media['file_samples'] if r['path'] == '/sys/kernel/debug/devices_deferred'],
                 original_powermgr_matching_records=len(driver['matching_battery_consumer_records']),
                 original_battery_path_log_observed=bool(driver['original_battery_real_path_records']),
                 backlight_readback_correlated=driver['backlight_hardware_readback_correlated'],
                 debugfs_mount_records=re.findall(r'^MEDIA141_DEBUGFS_.*$', text, re.M),
                 supplier145_results=[dict(module=m, status=int(s)) for m, s in re.findall(
                     r'^MEDIA145_SUPPLIER_RESULT module=(\w+) status=(\d+) binding_not_inferred=1$', text, re.M)],
                 supplier145_present=re.findall(r'^MEDIA145_SUPPLIER_PRESENT module=(\w+) binding_not_inferred=1$', text, re.M))
    output.open('x').write(json.dumps(media, indent=2))
    (report / 'driver-runtime-analysis-142.json').open('x').write(json.dumps(driver, indent=2))
    print(json.dumps({k: media[k] for k in ['run', 'phase_file', 'verified_file_count', 'alsa_card_observed',
        'alsa_pcm_observed', 'hci_class_observed', 'original_powermgr_matching_records', 'backlight_readback_correlated',
        'deferred_probe_samples', 'debugfs_mount_records']}, indent=2))
