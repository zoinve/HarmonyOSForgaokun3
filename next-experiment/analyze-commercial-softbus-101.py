"""Verify the observed SoftBus config/mapping and correlate native UI timing."""
from pathlib import Path
import hashlib
import json
import re
import runpy
import tarfile

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'next-experiment'


if __name__ == '__main__':
    folder = ROOT/'reports/commercial61-native-101'
    output = folder/'softbus-runtime-analysis.json'
    assert not output.exists()
    source = folder/'runtime-evidence'
    manifest = json.loads((source/'retrieval-manifest.json').read_text())
    assert manifest['physical_serial_guard_passed'] and manifest['original_udid_guard_passed']
    hashes = {}
    with tarfile.open(source/'original.tar') as archive:
        def load(name):
            with archive.extractfile('./'+name) as stream:
                body = stream.read()
            digest = hashlib.sha256(body).hexdigest()
            assert digest == manifest['files'][name]['sha256']
            assert len(body) == manifest['files'][name]['bytes']
            hashes[name] = digest
            return body
        diagnostic = load('snapshot075-commercial-desktop086.log')
        hilog = load('interactive-hilog030.log')
        phase = load(max((n for n in manifest['files'] if re.fullmatch(r'phase-\d+\.log', n)), key=lambda n: int(n.split('-')[1].split('.')[0])))
    text = diagnostic.decode(errors='replace').replace('\x00', '\n')
    samples = []
    for match in re.finditer(r'SOFTBUS101_SAMPLE target=(\d+)\n(.*?)SOFTBUS101_SAMPLE_END target=\1', text, re.S):
        target, body = match.groups()
        samples.append(dict(target=int(target),
            config_expected=re.findall(r'SOFTBUS101_CONFIG expected=(\d)', body),
            pid_records=re.findall(r'SOFTBUS101_PIDS values=([^\n]*)', body),
            mappings=[dict(pid=int(pid), readable=readable == '1', preload=present)
                      for pid, readable, present in re.findall(r'SOFTBUS101_MAPPING pid=(\d+) readable=(\d) platform_preload_present=(\w+)', body)]))
    tools = runpy.run_path(str(BASE/'audit-desktop-dispatch-100.py'))
    sanitize = runpy.run_path(str(BASE/'analyze-original-devicedetect-095.py'))['sanitize']
    rows = [row for number, line in enumerate(hilog.splitlines(), 1) if (row := tools['parse_line'](number, line))]
    scenes = sorted({row['pid'] for row in rows if b'BaseOobeManager: before start oobe end' in row['body']})
    queries = []
    for pid in scenes:
        pending = None
        for row in rows:
            if row['pid'] != pid or row['tid'] != pid:
                continue
            if b'device_picker_client.cpp:388]GetTrustedDeviceListWithAbilityFilter# start' in row['body']:
                if pending is not None:
                    queries.append(dict(pid=pid, start_line=pending['line'], end_line=None, ambiguous_nested_start=True))
                pending = row
            if b'device_picker_client.cpp:396]GetTrustedDeviceListWithAbilityFilter# end' in row['body'] and pending is not None:
                queries.append(dict(pid=pid, start_line=pending['line'], end_line=row['line'],
                                    elapsed_ms=tools['elapsed'](pending, row)))
                pending = None
        if pending is not None:
            queries.append(dict(pid=pid, start_line=pending['line'], end_line=None, elapsed_ms=None))
    lifecycle = [dict(line=row['line'], text=sanitize(row['body'])) for row in rows
                 if any(token in row['body'] for token in (b'OnSessionException: bundleName=com.huawei.hmos.hwstartupguide,',
                       b'BaseOobeManager: sessionExceptionCallback is called', b'BaseOobeManager: start oobe again'))]
    softbus = [dict(line=row['line'], text=sanitize(row['body'])) for row in rows
               if b'softbus_server/' in row['body'] and any(token in row['body'] for token in
                    (b'LnnGenerateCeParams# gen huks ce key fail', b'BusCenterServerDelayInit# try exceeds max times'))]
    result = dict(run=manifest['run'], verified_inputs=hashes, samples=samples, scene_pids=scenes,
        device_query_intervals=queries, original_lifecycle=lifecycle, softbus_early_key_failures=softbus,
        ram_config_marker_observed=b'SOFTBUS101_RAM_CONFIG' in phase,
        observer_started=b'SOFTBUS101_OBSERVER_BEGIN' in diagnostic,
        observer_completed=b'SOFTBUS101_OBSERVER_END' in diagnostic,
        all_five_config_and_mapping_samples_confirmed=len(samples) == 5 and all(
            s['config_expected'] == ['1'] and s['mappings'] and all(m['readable'] and m['preload'] == '0' for m in s['mappings']) for s in samples),
        original_oobe_relaunch_observed=any(b'BaseOobeManager: start oobe again' in row['body'] for row in rows),
        baseline_query_ms=21274, baseline_native_to_js_dispatch_ms=15747,
        baseline_live_mapping_not_recorded=True, causality_not_inferred_from_single_boot=True,
        desktop_verified=False, interaction_verified=False, original_evidence_modified=False)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps({k: v for k, v in result.items() if k not in ('original_lifecycle', 'softbus_early_key_failures', 'verified_inputs')}, indent=2))
