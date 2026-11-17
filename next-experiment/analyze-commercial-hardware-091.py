"""Report original API results and guard decisions without identity values."""
from pathlib import Path
import hashlib
import json
import re
import runpy

ROOT = Path(__file__).resolve().parent.parent


def analyze(body):
    text = body.decode('utf-8', errors='replace').replace('\x00', '\n')
    parameters = [dict(key=k, return_code=int(r), length=int(n)) for k, r, n in re.findall(
        r'HARDWARE091_PARAMETER key=(\S+) return=(-?\d+) length=(\d+) value_exported=0', text)]
    udid = [dict(phase=p, return_code=int(r), length=int(n), valid_hex64=bool(int(v))) for p, r, n, v in re.findall(
        r'HARDWARE091_GETDEVUDID phase=(\w+) return=(-?\d+) length=(\d+) valid_hex64=(\d+) value_exported=0', text)]
    actions = [int(n) for n in re.findall(r'HARDWARE091_DECISION action=(\d+)', text)]
    return dict(source_sha256=hashlib.sha256(body).hexdigest(), begin_observed='HARDWARE091_BEGIN' in text,
        end_observed='HARDWARE091_END' in text, original_parameters=parameters, original_udid_results=udid,
        firmware_records=re.findall(r'HARDWARE091_FIRMWARE[^\n]*', text), actions=actions,
        refusal_records=re.findall(r'HARDWARE091_REFUSED[^\n]*', text),
        serial_supply_returns=[int(n) for n in re.findall(r'HARDWARE091_SERIAL_SUPPLY original_public_api=1 return=(-?\d+)', text)],
        original_module_load_results=[bool(int(n)) for n in re.findall(r'HARDWARE091_ORIGINAL_MODULE loaded=(\d+)', text)],
        helper_exit_statuses=[int(n) for n in re.findall(r'HARDWARE091_RESULT exit_status=(\d+)', text)],
        no_identity_write_requested=bool(actions) and all(a == 0 or a >= 10 for a in actions),
        raw_identity_values_not_printed_by_helper=True, activation_completed_proven=False,
        desktop_verified=False, interaction_verified=False)


if __name__ == '__main__':
    folder = ROOT/'reports/commercial61-native-091'
    raw = folder/'runtime-evidence/raw'
    body = (raw/'snapshot075-commercial-desktop086.log').read_bytes()
    result = analyze(body)
    (folder/'hardware-runtime-analysis.json').open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    refresh = runpy.run_path(str(ROOT/'next-experiment/analyze-commercial-refresh-090.py'))['analyze']
    result = refresh(body, (raw/'interactive-hilog030.log').read_bytes())
    (folder/'network-refresh-runtime-analysis.json').open('x').write(json.dumps(result, indent=2))
