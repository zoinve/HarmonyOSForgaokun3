from collections import Counter
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'reports/commercial61-native-266'

if __name__ == '__main__':
    raw = REPORT / 'runtime-evidence/raw'
    phases = sorted(raw.glob('phase-*.log'), key=lambda p: int(p.stem.split('-')[1]))
    assert phases
    phase = phases[-1].read_bytes().decode(errors='replace')
    hilogs = list(raw.glob('*hilog*'))
    hilog = '\n'.join(p.read_bytes().decode(errors='replace') for p in hilogs)
    markers = ['RADIO261_ORIGINAL_HDF', 'NATIVE_QCA022 broker_listening=1',
               'NATIVE_QCA022 real_channel_open=1', 'NATIVE_QCA022 real_channel_open=0',
               'PERSISTENT166_READY', 'PERSISTENT166_REFUSED',
               'NATIVE_ORIGINAL_REFUSED', 'RADIO261_BROKER unavailable=1']
    errors = ['hci_interface_service not found', 'hdiInit failed',
              'startup_timer_expired', 'scanAp result false', 'IWifiScanCallback']
    result = dict(phase_snapshot=phases[-1].name,
        marker_counts={item: phase.count(item) for item in markers},
        original_blue_host_process_samples=len(re.findall(r'/vendor/bin/hdf_devhost -i 5 -n blue_host', phase)),
        old_launcher_samples=phase.count('/vendor/bin/l410_blue_host_fd_launcher'),
        scan_bss_counts=[int(n) for n in re.findall(r'RADIO261_SCAN_RESULTS bss_count=(\d+)', phase)],
        qca_commands=dict(Counter(re.findall(r'NATIVE_QCA022 command opcode=([0-9a-f]{4})', phase))),
        qca_completions=[dict(opcode=op, status=int(status)) for op, status in
            re.findall(r'NATIVE_QCA022 completion opcode=([0-9a-f]{4}) status=(\d+)', phase)],
        hilog_available=bool(hilogs), hilog_error_counts={item: hilog.count(item) for item in errors},
        system_scan_list_sizes=[int(n) for n in re.findall(r'GetScanInfoList, size: (\d+)', hilog)],
        bluetooth_ui_enable_verified=False, nearby_wifi_ui_verified=False,
        displayed_device_name_verified=False, raw_network_identities_exported=False)
    (REPORT / 'radio-analysis-274.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
