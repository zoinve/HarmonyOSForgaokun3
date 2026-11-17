"""Keep genuine association, kernel addressing and bridge reports separate."""
from pathlib import Path
import hashlib
import ipaddress
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def file_bodies(body, path):
    pattern = r'^NETWORK084_FILE_BEGIN path=' + re.escape(path) + r'\n(.*?)^NETWORK084_FILE_END path=' + re.escape(path) + r' bytes=\d+ complete_not_inferred=1$'
    return re.findall(pattern, body, re.MULTILINE | re.DOTALL)


def analyze(text):
    phases = []
    seen = set()
    pattern = r'^PHASE_BEGIN wifi-supplicant-(?P<mode>\w+)084\n(.*?)^PHASE_END wifi-supplicant-(?P=mode)084 status=(-?\d+)[ \t]*$'
    for block in re.finditer(pattern, text, re.MULTILINE | re.DOTALL):
        mode, body, status = block.groups()
        key = (mode, body, status)
        if key in seen:
            continue
        seen.add(key)
        context = re.search(r'^NETWORK084_TARGET_CONTEXT pid=(\d+) net_inode=(\d+) mnt_inode=(\d+) pid_inode=(\d+) root_verified=1 mode=' + re.escape(mode) + r' connectivity_not_inferred=1$', body, re.MULTILINE)
        phases.append(dict(mode=mode, status=int(status), context=tuple(map(int, context.groups())) if context else None,
                           output=body[context.end():] if context else body))
    starts = {row['context'] for row in phases if row['mode'] == 'start' and row['status'] == 0 and row['context']}
    admitted = [row for row in phases if row['status'] == 0 and row['context'] in starts]
    ready = ('NETWORK084_PRIVATE_CONFIG_VERIFIED_RAM_ONLY' in text and
             'NETWORK084_START_RESULT status=0 credentials_supplied=1 association_requested=1' in text and bool(starts))
    states = list(dict.fromkeys(state for row in admitted if row['mode'] == 'status'
                               for state in re.findall(r'^wpa_state=(\S+)$', row['output'], re.MULTILINE)))
    addresses, routes, netmanager, dhcp = [], [], [], []
    for row in admitted:
        if row['mode'] != 'network':
            continue
        for family, value, mask, flags in re.findall(r'^NETWORK084_ADDRESS interface=wlan0 family=(\d+) value=(\S+) netmask=(\S+) flags=(\d+)$', row['output'], re.MULTILINE):
            ip = ipaddress.ip_address(value)
            item = dict(family=int(family), address=str(ip), netmask=mask, flags=int(flags))
            if item not in addresses:
                addresses.append(item)
        for data in file_bodies(row['output'], '/proc/net/route'):
            for line in data.splitlines():
                fields = line.split()
                if len(fields) < 8 or fields[0] != 'wlan0':
                    continue
                try:
                    destination, gateway, flags = int(fields[1], 16), int(fields[2], 16), int(fields[3], 16)
                    if destination != 0 or flags & 3 != 3 or not gateway:
                        continue
                    gateway = str(ipaddress.IPv4Address(gateway.to_bytes(4, 'little')))
                except (ValueError, OverflowError):
                    continue
                item = dict(interface='wlan0', gateway=gateway, flags=flags)
                if item not in routes:
                    routes.append(item)
        for path, result in (('/data/local/tmp/l410-wifi-compat-v2/netmanager-v4.status', netmanager),
                             ('/data/local/tmp/l410-wifi-compat-v2/natural-control-v6.status', dhcp)):
            for data in file_bodies(row['output'], path):
                for line in data.splitlines():
                    if line and line not in result:
                        result.append(line)
    ipv4 = any(row['family'] == 2 and not any((ipaddress.ip_address(row['address']).is_unspecified,
               ipaddress.ip_address(row['address']).is_loopback, ipaddress.ip_address(row['address']).is_link_local,
               ipaddress.ip_address(row['address']).is_multicast)) for row in addresses)
    return dict(private_config_loaded_into_ram='NETWORK084_PRIVATE_CONFIG_VERIFIED_RAM_ONLY' in text,
                phase_status_records=[dict(mode=row['mode'], status=row['status'], context_verified=row['context'] is not None) for row in phases],
                original_supplicant_started_proven=ready, observed_wpa_states=states,
                actual_association_proven=ready and 'COMPLETED' in states,
                actual_interface_addresses=addresses, actual_ipv4_default_routes=routes,
                kernel_ipv4_address_and_default_route_proven=ready and ipv4 and bool(routes),
                original_netmanager_bridge_status_records=netmanager,
                original_dhcp_bridge_status_records=dhcp,
                original_bridge_publication_reported_success=any(re.fullmatch(r'stage=complete result=0 supplier=[1-9]\d*', line) for line in netmanager),
                original_bridge_dhcp_reported_complete=any(re.fullmatch(r'stage=dhcp(?:-cache)?-complete result=0', line) for line in dhcp),
                credentials_exported=False, association_requested=True,
                dns_resolution_proven=False, internet_reachability_proven=False,
                harmony_default_network_proven=False, oobe_completed_proven=False,
                desktop_visible_interaction_proven=False,
                target_timeout_recovered='COMMERCIAL084 target_timeout=1' in text,
                target_exit_records=list(dict.fromkeys(re.findall(r'^COMMERCIAL084_TARGET_EXIT .*$', text, re.MULTILINE))))


def main():
    folder = ROOT / 'reports/commercial61-native-084'
    paths = sorted((folder / 'runtime-evidence/raw').glob('phase-*.log'))
    assert paths, 'no recovered phase evidence'
    blob = paths[-1].read_bytes()
    result = analyze(blob.decode(errors='replace'))
    result.update(selected_cumulative_phase=paths[-1].name,
                  selected_phase_sha256=hashlib.sha256(blob).hexdigest(),
                  cumulative_snapshots_not_counted_as_repeated_operations=True)
    with (folder / 'network-analysis.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
