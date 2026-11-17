"""Correlate the original-layout repair with real events and scanout evidence."""
from pathlib import Path
import hashlib
import json
import re

B = Path(__file__).resolve().parents[1]
R = B / 'reports/commercial61-native-065'


def main():
    assert not (R / 'layout-analysis.json').exists(), 'Preserve numbered evidence'
    evidence = R / 'runtime-evidence'
    manifest = json.loads((evidence / 'retrieval-manifest.json').read_text())
    for name, item in manifest['files'].items():
        blob = (evidence / 'raw' / name).read_bytes()
        assert len(blob) == item['bytes'] and hashlib.sha256(blob).hexdigest() == item['sha256']
    native = sorted((evidence / 'raw').glob('phase-*.log'))[-1].read_bytes().decode(errors='replace')
    hilog = (evidence / 'raw/interactive-hilog030.log').read_bytes().decode(errors='replace')
    events = json.loads((R / 'event-analysis.json').read_text())
    account = json.loads((R / 'account-analysis.json').read_text())
    runtime = json.loads((R / 'runtime-analysis.json').read_text())
    assert events['run'] == account['run'] == runtime['run'] == manifest['run']
    previous = json.loads((B / 'reports/commercial61-native-064/event-analysis.json').read_text())
    keys = ['bootevent.hdf_devmgr.ready', 'bootevent.composer_host.ready',
            'bootevent.account.ready', 'bootevent.boot.completed']
    observations = {}
    for key in keys:
        values = [dict(round=r['round'], output=v['output'], command_result=v['result'],
                       actual_value_true=v['output'].strip() == 'true')
                  for r in events['rounds'] for v in r['values'] if v['key'] == key]
        prior = [v['output'] for r in previous['rounds'][-1:] for v in r['values'] if v['key'] == key]
        writes = [line for line in hilog.splitlines()
                  if re.search(r'SystemSetParameter name ' + re.escape(key) + r' id:\d+ ret:', line)]
        observations[key] = dict(read_observations=values, previous064_final_output=prior,
                                 original_external_setter_logs=writes)
    release = [line for line in hilog.splitlines()
               if 'Release RsNode' in line or 'read boot completed is true' in line]
    captures = runtime['captures']
    result = dict(run=manifest['run'], verified_files=len(manifest['files']),
                  original_alias_restore_markers=[line for line in native.splitlines()
                      if 'COMMERCIAL065_ROOT_LAYOUT path=/chipset target=/vendor' in line],
                  parameter_observations=observations,
                  complete_event_rounds=events['complete_expected_rounds'],
                  original_account_success_callbacks=account['original_account_success_callbacks'],
                  bootanimation_release_or_completion_logs=release,
                  captures=captures,
                  sparse_nonblack_sample_seen=any(c.get('nonblack_pixels', 0) > 0 for c in captures),
                  full_resolution_desktop_verified=False, interaction_verified=False,
                  boot_completion_not_desktop_proof=True, missing_logs_not_nonexecution_proof=True)
    (R / 'layout-analysis.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
