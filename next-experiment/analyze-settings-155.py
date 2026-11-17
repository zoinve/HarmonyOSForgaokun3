"""Correlate Settings install rejection and launch failures without changing policy."""
from pathlib import Path
import hashlib
import io
import json
import re
import runpy
import zipfile

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = 'com.huawei.hmos.settings'


def summarize(text):
    lines = text.splitlines()
    launches = []
    install_failures = []
    for index, line in enumerate(lines):
        if 'hap file verify failed, bundlePath: /system/app/Settings/Settings.hap' in line:
            # Installation work is correlated by the BMS worker PID/TID, not nearby noise.
            parts = line.split()
            worker = parts[2:4]
            nearby = [(i + 1, candidate) for i, candidate in enumerate(lines[max(0, index - 16):index + 9], max(0, index - 16))
                      if candidate.split()[2:4] == worker]
            install_failures.append(dict(line=index + 1, message=line,
                signing_block_missing=any('No HAP Signing Block before ZIP Central Directory' in value for _, value in nearby),
                signature_error_8519742=any('signature info failed 8519742' in value for _, value in nearby),
                context=[dict(line=i, message=value) for i, value in nearby]))
        if 'StartAbility ability:' + BUNDLE + '/' not in line:
            continue
        nearby = lines[index + 1:index + 100]
        # Trace IDs link foundation errors even when unrelated logs interleave.
        trace_match = next((re.search(r'\[([0-9a-f]+) [0-9a-f]+ 0\]', candidate)
                            for candidate in nearby if 'bundle not exist -n ' + BUNDLE + ' -u 100 ' in candidate), None)
        trace = trace_match.group(1) if trace_match else None
        matching = [(index + offset + 2, candidate) for offset, candidate in enumerate(nearby)
                    if trace and '[' + trace + ' ' in candidate]
        launches.append(dict(line=index + 1, message=line, trace=trace,
            bundle_absent_user100=any('bundle not exist -n ' + BUNDLE + ' -u 100 ' in value for _, value in matching),
            ability_request_error_2097152=any('generate ability request local error:2097152' in value for _, value in matching),
            context=[dict(line=i, message=value) for i, value in matching
                     if any(token in value for token in ['bundle not exist', 'ExplicitQueryAbility no match', 'local error:', 'StartAbilityByFreeInstall error:'])]))
    return dict(settings_install_failures=install_failures, settings_launches=launches,
        correlated_missing_bundle_launch_count=sum(row['bundle_absent_user100'] and row['ability_request_error_2097152'] for row in launches),
        settings_ui_success_verified=False, physical_touch_failure_inferred=False,
        pcsettings_is_not_assumed_to_replace_settings=True)


def inspect_hap(read, image, path):
    data = read(image, 'cat ' + path)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        metadata = {}
        for name in ['module.json', 'config.json', 'pack.info']:
            if name in archive.namelist():
                metadata[name] = json.loads(archive.read(name))
        # Record bytes, not a substitute for the original signature verifier.
        preceding = data[max(0, archive.start_dir - 32):archive.start_dir]
        return dict(path=path, bytes=len(data), sha256=hashlib.sha256(data).hexdigest(),
            zip_entries=len(archive.infolist()), central_directory_offset=archive.start_dir,
            preceding_32_bytes_hex=preceding.hex(), metadata=metadata,
            offline_signature_verification_performed=False)


if __name__ == '__main__':
    folder = ROOT / 'reports/settings-diagnostics-155'
    assert not folder.exists(), 'immutable report already exists'
    evidence = ROOT / 'reports/commercial61-native-153/runtime-evidence'
    manifest = json.loads((evidence / 'retrieval-manifest.json').read_text())
    for name, expected in manifest['files'].items():
        data = (evidence / 'raw' / name).read_bytes()
        assert len(data) == expected['bytes'] and hashlib.sha256(data).hexdigest() == expected['sha256'], name
    log = evidence / 'raw/interactive-hilog030.log'
    result = summarize(log.read_text(errors='replace'))
    api = runpy.run_path(str(ROOT / 'next-experiment/audit-board-driver-contracts-126.py'))
    image = api['IMAGES'] / 'p111-system.kr990-ext4-v1.img'
    result.update(run=manifest['run'], verified_evidence_files=len(manifest['files']),
        hilog_file=str(log.relative_to(ROOT)), hilog_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),
        source_image=str(image), source_image_opened_read_only=True, target_modified=False,
        signature_checks_changed=False, developer_mode_changed=False, live_debug_connection_verified=False,
        original_haps=[inspect_hap(api['read'], image, path) for path in
                       ['/system/app/Settings/Settings.hap', '/system/app/PCSettings/PCSettings.hap']],
        original_hdcd_config=json.loads(api['read'](image, 'cat /system/etc/init/hdcd.cfg')))
    folder.mkdir()
    (folder / 'result.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(dict(install_failures=len(result['settings_install_failures']),
        launch_requests=len(result['settings_launches']),
        correlated_missing_bundle_launch_count=result['correlated_missing_bundle_launch_count'],
        haps=[dict(path=row['path'], sha256=row['sha256'], metadata_files=list(row['metadata'])) for row in result['original_haps']]), indent=2))
