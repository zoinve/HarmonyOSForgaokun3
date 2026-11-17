"""Require native namespace/log evidence as well as authenticated client success."""
from pathlib import Path
import hashlib
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]


def summarize(text, client):
    contexts = [dict(target=int(pid),net_inode=int(inode)) for pid,inode in re.findall(
        r'^LIVE157_CONTEXT target=(\d+) net_inode=(\d+) separate_mount_pid_namespaces=1 readonly_logs=1 pid1=1 address=192\.168\.10\.210 port=22257$',text,re.M)]
    network = [dict(target=int(pid),net_inode=int(inode)) for pid,inode in re.findall(
        r'^NETWORK084_TARGET_CONTEXT pid=(\d+) net_inode=(\d+) mnt_inode=\d+ pid_inode=\d+ root_verified=1 mode=network connectivity_not_inferred=1$',text,re.M)]
    matching = [row for row in contexts if row in network]
    load = [int(status) for status in re.findall(r'^LIVE157_LOAD status=(-?\d+) optional_sidecar=1 original_runtime_unchanged=1$',text,re.M)]
    ends = [dict(status=int(status),reaped=True) for status in re.findall(r'^LIVE157_END status=(\d+) namespace_reaped=1$',text,re.M)]
    stops = [dict(supervisor=int(pid),reaped=int(reaped),state=int(state)) for pid,reaped,state in re.findall(
        r'^LIVE157_STOP supervisor=(\d+) reaped=([01]) state=(\d+)$',text,re.M)]
    accepted = load == [0] and len(contexts) == 1 and len(matching) == 1
    accepted = accepted and all(client.get(key) is True for key in ['authenticated_native_candidate_connected',
        'hilog_grew_during_connection','live_follow_protocol_completed','arbitrary_shell_refused']) and 'error' not in client
    return dict(load_results=load,contexts=contexts,matching_original_network_contexts=matching,ends=ends,stops=stops,
        authenticated_native_readonly_channel_verified=accepted,
        full_process_debugger_attached=False,settings_ui_repaired=False,
        physical_input_or_usb_service_acceptance_inferred=False)


if __name__ == '__main__':
    report = ROOT / 'reports/commercial61-native-157'
    output = report / 'live-runtime-analysis-157.json'
    assert not output.exists()
    evidence = report / 'runtime-evidence'
    manifest = json.loads((evidence / 'retrieval-manifest.json').read_text())
    for name,row in manifest['files'].items():
        data = (evidence / 'raw' / name).read_bytes()
        assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256'],name
    latest = max((n for n in manifest['files'] if re.fullmatch(r'phase-\d+\.log',n)),key=lambda n:int(n[6:-4]))
    text = (evidence / 'raw' / latest).read_text(errors='replace')
    client = json.loads((report / 'live-client-observation.json').read_text())
    result = summarize(text,client)
    input_summary = runpy.run_path(str(ROOT / 'next-experiment/analyze-input-usb-148.py'))['summarize'](text)
    result.update(run=manifest['run'],verified_file_count=len(manifest['files']),phase_file=latest,
        client_observation=client,native_mmi_holds_touchscreen=input_summary['native_mmi_holds_touchscreen'],
        storage_modules_live=input_summary['storage_modules_live'],
        original_settings_diagnosis=runpy.run_path(str(ROOT / 'next-experiment/analyze-settings-155.py'))['summarize'](
            (evidence / 'raw/interactive-hilog030.log').read_text(errors='replace')))
    output.open('x').write(json.dumps(result,indent=2))
    print(json.dumps({key:result[key] for key in ['run','verified_file_count','load_results','contexts',
        'matching_original_network_contexts','ends','stops','authenticated_native_readonly_channel_verified',
        'native_mmi_holds_touchscreen','storage_modules_live']},indent=2))
