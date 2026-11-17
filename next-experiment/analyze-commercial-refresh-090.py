"""Separate CLI requests, real WPA states and original guide callbacks."""
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parent.parent


def analyze(body, hilog):
    text = body.decode('utf-8', errors='replace').replace('\x00', '\n')
    native = hilog.decode('utf-8', errors='replace')
    before = re.search(r'REFRESH090_STATUS_BEFORE_BEGIN\n(.*?)REFRESH090_STATUS_BEFORE_END exit_status=(\d+)', text, re.S)
    disconnected = re.search(r'REFRESH090_STATUS_DISCONNECTED_BEGIN\n(.*?)REFRESH090_STATUS_DISCONNECTED_END exit_status=(\d+)', text, re.S)
    after = re.findall(r'REFRESH090_STATUS_AFTER_BEGIN target=(\d+)\n(.*?)REFRESH090_STATUS_AFTER_END target=\1 exit_status=(\d+)', text, re.S)
    def state(block):
        match = re.search(r'^wpa_state=(\S+)\s*$', block, re.M)
        return match.group(1) if match else None
    samples = [dict(target=int(target), wpa_state=state(block), exit_status=int(status)) for target, block, status in after]
    callbacks = [line for line in native.splitlines() if '/HwStartupGuide:' in line and
                 re.search(r'InternetManager:(net |hasDefaultNet|wait net validate)', line)]
    result = dict(script_sha256=hashlib.sha256(body).hexdigest(), hilog_sha256=hashlib.sha256(hilog).hexdigest(),
        begin_observed='REFRESH090_BEGIN' in text, end_observed='REFRESH090_END' in text,
        refused=re.findall(r'REFRESH090_REFUSED[^\n]*', text),
        disconnect_requests=len(re.findall(r'^REFRESH090_DISCONNECT_BEGIN$', text, re.M)),
        reconnect_requests=len(re.findall(r'^REFRESH090_RECONNECT_BEGIN ', text, re.M)),
        disconnect_statuses=[int(n) for n in re.findall(r'REFRESH090_DISCONNECT_RESULT exit_status=(\d+)', text)],
        reconnect_statuses=[int(n) for n in re.findall(r'REFRESH090_RECONNECT_RESULT exit_status=(\d+)', text)],
        before_state=state(before.group(1)) if before else None,
        disconnected_state=state(disconnected.group(1)) if disconnected else None,
        after_samples=samples, original_guide_network_records=callbacks,
        cli_zero_is_not_reply_or_connectivity_proof=True,
        oobe_completed_proven=False, desktop_verified=False, interaction_verified=False)
    result['observed_completed_disconnected_completed'] = (
        result['before_state'] == 'COMPLETED' and result['disconnected_state'] == 'DISCONNECTED' and
        bool(samples) and all(s['exit_status'] == 0 and s['wpa_state'] == 'COMPLETED' for s in samples))
    return result


if __name__ == '__main__':
    folder = ROOT / 'reports/commercial61-native-090'
    raw = folder / 'runtime-evidence/raw'
    result = analyze((raw/'snapshot075-commercial-desktop086.log').read_bytes(), (raw/'interactive-hilog030.log').read_bytes())
    (folder/'network-refresh-runtime-analysis.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
