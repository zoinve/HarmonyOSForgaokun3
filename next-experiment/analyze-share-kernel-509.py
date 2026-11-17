"""Separate real native P2P control readiness from sharing acceptance."""
from pathlib import Path
import json
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'next-experiment'
READER = runpy.run_path(str(BASE / 'compress-historical-logs-226.py'))['open_log']


def inspect(stream):
    phases = []
    active = None
    start_results = []
    resin_lines = []
    gpio_lines = []
    for index, raw in enumerate(stream, 1):
        line = raw.decode(errors='replace').strip()
        begin = re.fullmatch(r'PHASE_BEGIN wifi-supplicant-(share-start|share-observe)086', line)
        if begin:
            active = dict(mode=begin[1], namespace_verified=False, pong=False,
                          interface_results=[], supplicant_results=[], line=index)
            phases.append(active)
        if active:
            context = re.fullmatch(r'NETWORK084_TARGET_CONTEXT pid=(\d+) net_inode=(\d+) mnt_inode=(\d+) pid_inode=(\d+) root_verified=1 mode=' + active['mode'] + r' connectivity_not_inferred=1', line)
            if context:
                active['namespace_verified'] = all(int(value) > 0 for value in context.groups())
            match = re.fullmatch(r'SHARE501_INTERFACE_ADD result=(\d+) real_netdev_required=1', line)
            if match: active['interface_results'].append(int(match[1]))
            match = re.fullmatch(r'SHARE501_SUPPLICANT_START result=(\d+) group_connected_not_inferred=1', line)
            if match: active['supplicant_results'].append(int(match[1]))
            match = re.fullmatch(r'SHARE501_PING pong=([01]) errno=\d+ transfer_verified=0', line)
            if match: active['pong'] = match[1] == '1'
            end = re.fullmatch(r'PHASE_END wifi-supplicant-' + active['mode'] + r'086 status=(\d+)', line)
            if end:
                active['exit_status'] = int(end[1])
                active = None
        match = re.fullmatch(r'SHARE502_START_RESULT status=(\d+) transfer_verified=0', line)
        if match: start_results.append(int(match[1]))
        if re.search(r'input: pmic_resin as |N: Name="pmic_resin"', line): resin_lines.append(index)
        if re.search(r'input: gpio-keys as |N: Name="gpio-keys"', line): gpio_lines.append(index)
    ready = any(row['mode'] == 'share-start' and row['namespace_verified'] and row['pong']
                and row.get('exit_status') == 0 and row['interface_results'] == [0]
                and row['supplicant_results'] == [0] for row in phases)
    return dict(phases=phases, start_results=start_results,
        real_native_p2p_control_ready=ready, pmic_resin_input_lines=resin_lines,
        gpio_keys_input_lines=gpio_lines, physical_volume_down_verified=False,
        memory_limit_enforcement_verified=False, p2p_group_handshake_verified=False,
        huawei_share_file_transfer_verified=False, raw_peer_data_exported=False)


if __name__ == '__main__':
    report = ROOT / 'reports/commercial61-native-502'
    output = report / 'share-kernel-analysis-509.json'
    assert not output.exists()
    manifest = json.loads((report / 'runtime-evidence/retrieval-manifest.json').read_text())
    phases = [name for name in manifest['files'] if re.fullmatch(r'phase-\d+\.log', name)]
    phase = max(phases, key=lambda name: int(re.search(r'\d+', name)[0]))
    with READER(report / 'runtime-evidence/raw' / phase) as stream: result = inspect(stream)
    cpu = runpy.run_path(str(BASE / 'analyze-cpufreq-native-484.py'))
    with READER(report / 'runtime-evidence/raw' / phase) as stream:
        result['cpu'] = cpu['phase_inspect'](stream)
    with READER(report / 'runtime-evidence/raw/interactive-hilog030.log') as stream:
        result['cpu'].update(cpu['reader_inspect'](stream))
    share = runpy.run_path(str(BASE / 'analyze-share-492.py'))
    with READER(report / 'runtime-evidence/raw/interactive-hilog030.log') as stream:
        result['original_share_functions'] = share['inspect'](stream)
    result.update(run=manifest['run'],phase_file=phase)
    output.open('x').write(json.dumps(result,indent=2) + '\n')
    print(json.dumps({key:value for key,value in result.items() if key not in ['cpu','original_share_functions']},indent=2))
