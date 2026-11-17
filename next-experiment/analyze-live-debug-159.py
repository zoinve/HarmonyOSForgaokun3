"""Correlate authenticated dynamic endpoint, native namespace and cleanup evidence."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def summarize(text, client):
    contexts = [dict(target=int(pid),net_inode=int(inode),address=address) for pid,inode,address in re.findall(
        r'^LIVE159_CONTEXT target=(\d+) net_inode=(\d+) separate_mount_pid_namespaces=1 readonly_logs=1 pid1=1 address=(192\.168\.10\.\d{1,3}) port=22257 discovery_port=22259$',text,re.M)]
    network = [(int(pid),int(inode)) for pid,inode in re.findall(
        r'^NETWORK084_TARGET_CONTEXT pid=(\d+) net_inode=(\d+) mnt_inode=\d+ pid_inode=\d+ root_verified=1 mode=network connectivity_not_inferred=1$',text,re.M)]
    matching = [row for row in contexts if (row['target'],row['net_inode']) in network]
    load = [int(status) for status in re.findall(r'^LIVE159_LOAD status=(-?\d+) optional_sidecar=1 original_runtime_unchanged=1$',text,re.M)]
    ends = [dict(status=int(status),reaped=True) for status in re.findall(r'^LIVE159_END status=(\d+) namespace_reaped=1$',text,re.M)]
    stops = [dict(supervisor=int(pid),reaped=int(reaped),state=int(state)) for pid,reaped,state in re.findall(
        r'^LIVE159_STOP supervisor=(\d+) reaped=([01]) state=(\d+)$',text,re.M)]
    accepted = load == [0] and len(contexts) == 1 and len(matching) == 1
    accepted = accepted and contexts[0]['address'] == client.get('connected_address')
    accepted = accepted and len(ends) == 1 and ends[0]['status'] == 0 and len(stops) == 1 and stops[0]['reaped'] == 1
    accepted = accepted and all(client.get(key) is True for key in ['authenticated_native_candidate_connected',
        'discovered_endpoint_pinned_ssh_authenticated','hilog_grew_during_connection','live_follow_protocol_completed',
        'arbitrary_shell_refused']) and 'error' not in client
    return dict(load_results=load,contexts=contexts,matching_original_network_contexts=matching,ends=ends,stops=stops,
        authenticated_native_readonly_channel_verified=accepted,
        full_process_debugger_attached=False,settings_ui_repaired=False,
        physical_input_or_usb_service_acceptance_inferred=False)


if __name__ == '__main__':
    # Reuse immutable retrieval hashing and driver analysis, not fixed-address acceptance.
    base = (ROOT / 'next-experiment/analyze-live-debug-157.py').read_text()
    start = base.index('def summarize(')
    end = base.index("\n\nif __name__ == '__main__':",start)
    base = base[:start] + base[end:]
    base = base.replace('commercial61-native-157','commercial61-native-159').replace('live-runtime-analysis-157.json','live-runtime-analysis-159.json')
    exec(compile(base,'analyze-live-debug-159.generated.py','exec'),{'__name__':'__main__','__file__':__file__,'summarize':summarize})
