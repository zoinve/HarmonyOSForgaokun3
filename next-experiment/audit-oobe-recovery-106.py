"""Audit original recovery ordering offline; never boot or alter target state."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'reports/oobe-recovery-audit-106'


def events(text, scene_pid):
    rules = {
        'force_stop_success': 'force stop process successfully.',
        'ams_guide_died': 'On ability died: /com.huawei.hmos.hwstartupguide/',
        'wms_guide_exception': 'OnSessionException: bundleName=com.huawei.hmos.hwstartupguide,',
        'query_end': 'GetTrustedDeviceListWithAbilityFilter# end',
        'recovery_callback': 'sessionExceptionCallback is called',
        'guide_relaunch': 'BaseOobeManager: start oobe again',
    }
    found = {key: [] for key in rules}
    for number, line in enumerate(text.splitlines(), 1):
        match = re.match(r'\d\d-\d\d (\d\d):(\d\d):(\d\d)\.(\d{3})\s+(\d+)\s+', line)
        if not match:
            continue
        h, m, s, ms, pid = map(int, match.groups())
        for key, needle in rules.items():
            if needle not in line:
                continue
            if key in {'wms_guide_exception', 'query_end', 'recovery_callback', 'guide_relaunch'} and pid != scene_pid:
                continue
            found[key].append(dict(line=number, milliseconds=((h * 60 + m) * 60 + s) * 1000 + ms,
                                   text=line))
    return found


def main():
    assert not OUT.exists(), 'Preserve numbered evidence'
    base = ROOT / 'reports/commercial61-native-105'
    reference = json.loads((base / 'reference-runtime-analysis.json').read_text())
    log = base / 'runtime-evidence/raw/interactive-hilog030.log'
    data = log.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    assert sha == reference['verified_input_sha256'][log.name]
    timing = json.loads((base / 'server-capture-timing.json').read_text())
    text = data.decode('utf-8', errors='replace')
    found = events(text, timing['scene_pid'])
    assert all(len(value) == 1 for value in found.values()), 'Ambiguous recovery chain'
    order = ['force_stop_success', 'ams_guide_died', 'wms_guide_exception',
             'query_end', 'recovery_callback', 'guide_relaunch']
    timestamps = [found[key][0]['milliseconds'] for key in order]
    assert timestamps == sorted(timestamps), 'Unexpected event order'
    decoded_path = ROOT / 'reports/sceneboard-oobe-audit-097/decoded-methods.json'
    decoded_bytes = decoded_path.read_bytes()
    decoded = json.loads(decoded_bytes)
    methods = [entry for entry in decoded['methods'] if '/oobe/BaseOobeManager&' in entry['record']]
    before = next(entry for entry in methods if entry['method']['name'].endswith('#beforeStartOobe'))
    callback = next(entry for entry in methods if entry['method']['name'] == '#~@0=@0*#')
    def operands(entry):
        return [operand.get('string') for insn in entry['instructions'] for operand in insn['operands']
                if operand.get('string') is not None]
    before_names, callback_names = operands(before), operands(callback)
    assert 'registerSessionExceptionListener' in before_names
    assert 'isOobeActivated' in callback_names and 'isTrustlistForWms' in callback_names
    assert 'startOobeAbility' in callback_names
    result = dict(
        run=reference['run'], hilog_sha256=sha,
        utf8_replacement_characters=text.count(chr(0xfffd)),
        decoded_methods_sha256=hashlib.sha256(decoded_bytes).hexdigest(),
        timeline=found,
        exception_to_callback_ms=timestamps[4] - timestamps[2],
        query_return_to_callback_ms=timestamps[4] - timestamps[3],
        listener_registered_before_original_guide_start=True,
        callback_checks_oobe_state_and_trustlist=True,
        callback_has_original_restart_call=True,
        inference='Main-thread delay deferred exception handling; delay alone is not evidence of why recovery exists.',
        reference_success_runtime_equivalence_proven=False,
        changed_original_state=False, operational_boot_performed=False,
        desktop_verified=False)
    OUT.mkdir()
    with (OUT / 'result.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
