"""Require matching target context, completed phases and real curl success."""
from pathlib import Path
import hashlib
import ipaddress
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def phases(text):
    result, seen = [], set()
    pattern = r'^PHASE_BEGIN wifi-supplicant-(?P<mode>\w+)085\n(.*?)^PHASE_END wifi-supplicant-(?P=mode)085 status=(-?\d+)[ \t]*$'
    for match in re.finditer(pattern, text, re.MULTILINE | re.DOTALL):
        mode, body, status = match.groups()
        if (mode, body, status) in seen:
            continue
        seen.add((mode, body, status))
        context = re.search(r'^NETWORK084_TARGET_CONTEXT pid=(\d+) net_inode=(\d+) mnt_inode=(\d+) pid_inode=(\d+) root_verified=1 mode=' + re.escape(mode) + r' connectivity_not_inferred=1$', body, re.MULTILINE)
        result.append(dict(mode=mode, body=body, status=int(status), context=tuple(map(int, context.groups())) if context else None))
    return result


def analyze(text):
    rows = phases(text)
    starts = {row['context'] for row in rows if row['mode'] == 'start' and row['status'] == 0 and row['context']}
    ready = bool(starts) and 'NETWORK084_PRIVATE_CONFIG_VERIFIED_RAM_ONLY' in text
    probes, files = [], []
    for row in rows:
        valid = ready and row['status'] == 0 and row['context'] in starts
        if row['mode'] in ('http', 'https'):
            values = re.findall(r'^NETWORK085_CURL http_code=(\d{3}) remote_ip=(\S+) namelookup=([0-9.]+) ssl_verify_result=(\d+)$', row['body'], re.MULTILINE)
            marker = 'NETWORK085_PROBE mode=' + row['mode'] + ' original_curl=1 tls_bypass=0 success_not_inferred=1'
            good = False
            if len(values) == 1:
                code, peer, timing, tls = values[0]
                try:
                    address = ipaddress.ip_address(peer)
                    good = not (address.is_loopback or address.is_unspecified or address.is_link_local or address.is_multicast)
                except ValueError:
                    good = False
                good = good and code == '204' and (row['mode'] != 'https' or tls == '0')
            probes.append(dict(mode=row['mode'], exit_status=row['status'], context_verified=valid,
                               curl_fields=values, success_proven=bool(valid and marker in row['body'] and good)))
        if row['mode'] == 'freeze' and valid:
            pattern = r'^FREEZE085_FILE_BEGIN name=(\S+) size=(\d+)\n(.*?)^FREEZE085_FILE_END bytes=(\d+) complete_not_inferred=1$'
            for name, declared, body, captured in re.findall(pattern, row['body'], re.MULTILINE | re.DOTALL):
                item = dict(name=name, declared_bytes=int(declared), captured_bytes=int(captured),
                            body_sha256=hashlib.sha256(body.encode()).hexdigest(),
                            declared_size_equals_capture=int(declared) == int(captured))
                if item not in files:
                    files.append(item)
    return dict(probe_records=probes, original_freeze_file_records=files,
                independent_http_204_proven=any(p['mode'] == 'http' and p['success_proven'] for p in probes),
                independent_https_204_tls_verification_proven=any(p['mode'] == 'https' and p['success_proven'] for p in probes),
                named_url_platform_resolution_only_not_packet_level_dns=True,
                original_freeze_stacks_captured=any(row['name'].endswith('_stack') for row in files),
                oobe_completed_proven=False, desktop_visible_interaction_proven=False)


def main():
    folder = ROOT / 'reports/commercial61-native-085'
    paths = sorted((folder / 'runtime-evidence/raw').glob('phase-*.log'))
    assert paths
    blob = paths[-1].read_bytes()
    result = analyze(blob.decode(errors='replace'))
    result.update(source_name=paths[-1].name, source_sha256=hashlib.sha256(blob).hexdigest())
    with (folder / 'probe-freeze-analysis.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
