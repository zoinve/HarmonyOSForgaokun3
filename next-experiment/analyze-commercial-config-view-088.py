"""Read genuine app-root hashes and original config/Dock lifecycle messages."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def observations(text, expected_hash):
    records = []
    pattern = (r'^CONFIG088_PATH_BEGIN pid=(\d+) path=(\S+)\n(.*?)'
               r'^CONFIG088_PATH_END pid=\1 path=\2$')
    for match in re.finditer(pattern, text, re.MULTILINE | re.DOTALL):
        pid, path, body = match.groups()
        stat_status = re.search(r'^CONFIG088_STAT_RESULT status=(\d+)$', body, re.MULTILINE)
        hash_status = re.search(r'^CONFIG088_HASH_RESULT status=(\d+)$', body, re.MULTILINE)
        digest = re.search(r'^([a-f0-9]{64})\s+/proc/' + pid + '/root' + re.escape(path) + '$', body, re.MULTILINE)
        records.append(dict(pid=int(pid), path=path,
                            stat_output=body.split('CONFIG088_STAT_RESULT', 1)[0].strip(),
                            stat_exit=int(stat_status[1]) if stat_status else None,
                            hash_exit=int(hash_status[1]) if hash_status else None,
                            sha256=digest[1] if digest else None,
                            expected_file_hash_observed=bool(digest and digest[1] == expected_hash and hash_status and hash_status[1] == '0')))
    return records


def main():
    folder = ROOT / 'reports/commercial61-native-088'
    raw = folder / 'runtime-evidence/raw'
    retrieval = json.loads((raw.parent / 'retrieval-manifest.json').read_text())
    assert retrieval['run'].startswith('commercial61-native-087-')
    prior = json.loads((ROOT / 'reports/commercial61-native-087/runtime-evidence/retrieval-manifest.json').read_text())
    assert retrieval['run'] != prior['run']
    for name, expected in retrieval['files'].items():
        blob = (raw / name).read_bytes()
        assert len(blob) == expected['bytes'] and hashlib.sha256(blob).hexdigest() == expected['sha256']
    hilog = (raw / 'interactive-hilog030.log').read_text(errors='replace')
    diagnostic = raw / 'snapshot075-commercial-desktop086.log'
    text = diagnostic.read_text(errors='replace') if diagnostic.exists() else ''
    provenance = json.loads((folder / 'config-provenance.json').read_text())
    rows = observations(text, provenance['workspace_sha256'])
    patterns = {
        'config_discovery': r'GetLayoutInfoFromConfig:|SmartDockLayoutConfig:|init from config length:',
        'dock_missing_apps': r'appDataFromSystem is empty, bundleName:',
        'dock_finished': r'getResidentList send EVENT_SMARTDOCK_INIT_FINISHED',
        'guide_network_timeouts': r'InternetManager:wait net validate time out\. jump to wlan page',
        'guide_start': r'BaseOobeManager: start oobe',
        'app_freeze_mentions': r'THREAD_BLOCK_3S|THREAD_BLOCK_6S|APP_FREEZE|appfreeze_handle',
    }
    highlights = {key: [dict(line=index, text=line) for index, line in enumerate(hilog.splitlines(), 1)
                        if re.search(pattern, line)] for key, pattern in patterns.items()}
    pids = sorted({int(m[1]) for m in re.finditer(r'^\S+\s+\S+\s+(\d+)\s+\d+\s+[A-Z]\s+\S*com\.ohos\.sceneboard/', hilog, re.MULTILINE)})
    for row in rows:
        row['pid_in_native_sceneboard_logs'] = row['pid'] in pids
    policy = re.search(r'^CONFIG088_POLICY_PARAMETER_BEGIN\n(.*?)^CONFIG088_POLICY_PARAMETER_END status=(\d+)$',
                       text, re.MULTILINE | re.DOTALL)
    consumption = bool(re.search(r'GetLayoutInfoFromConfig: getAllLayOutConfigFile end,finalLayout\.layoutInfo\.length 1\b', hilog)
                       and re.search(r'SmartDockLayoutConfig: convertAppLayout2DockLayout end, dockAppList length : 1\b', hilog))
    result = dict(run=retrieval['run'], entry='commercial61-native-088.conf', inherited_core='087',
                  unique_raw_run_not_prior087=True, verified_files=len(retrieval['files']),
                  diagnostic_088_marker_observed='CONFIG088_BEGIN' in text,
                  policy_parameter_output=policy[1].strip() if policy else None,
                  policy_parameter_exit=int(policy[2]) if policy else None,
                  path_observations=rows, config_read_and_conversion_logs_observed=consumption,
                  observed_sceneboard_pids=pids, highlights=highlights,
                  native_hilog_sha256=hashlib.sha256((raw / 'interactive-hilog030.log').read_bytes()).hexdigest(),
                  desktop_visible_interaction_proven=False, oobe_completed_proven=False)
    (folder / 'config-view-runtime-analysis.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps({key: value for key, value in result.items() if key != 'highlights'}, indent=2))
    print(json.dumps({key: len(value) for key, value in highlights.items()}, indent=2))


if __name__ == '__main__':
    main()
