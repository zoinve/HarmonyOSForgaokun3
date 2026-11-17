"""Summarize scoped radio markers without exporting peripheral identities."""
from pathlib import Path
import json
import re
import runpy
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
OPEN = runpy.run_path(str(BASE / 'compress-historical-logs-226.py'))['open_log']

if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in ['294', '297']
    candidate = sys.argv[1]
    report = ROOT / ('reports/commercial61-native-' + candidate)
    output = report / 'radio-analysis-302.json'
    assert not output.exists(), 'preserve numbered evidence'
    evidence = report / 'runtime-evidence'
    manifest = json.loads((evidence / 'retrieval-manifest.json').read_text())
    phases = [name for name in manifest['files'] if re.fullmatch(r'phase-\d+\.log', name)]
    phase = max(phases, key=lambda name: int(name[6:-4]))
    with OPEN(evidence / 'raw' / phase) as stream:
        text = stream.read().decode(errors='replace')
    markers = [line for line in text.splitlines() if line.startswith(
        ('RADIO294_', 'RADIO297_', 'NATIVE_BT022 ', 'NATIVE_QCA022 '))]
    with OPEN(evidence / 'raw/interactive-hilog030.log') as stream:
        hilog = stream.read().decode(errors='replace')
    commands = re.findall(r'NATIVE_QCA022 command opcode=([0-9a-f]+) bytes=(\d+)', text)
    completions = re.findall(r'NATIVE_QCA022 completion opcode=([0-9a-f]+) status=(\d+) bytes=(\d+)', text)
    result = dict(candidate=candidate, run=manifest['run'], phase=phase,
        scoped_markers=markers,
        real_channel_open_successes=text.count('NATIVE_QCA022 real_channel_open=1'),
        commands=[dict(opcode=op, bytes=int(size)) for op,size in commands],
        completions=[dict(opcode=op, status=int(status), bytes=int(size)) for op,status,size in completions],
        original_power_on_failures=hilog.count('vendorInterface_->op BT_OP_POWER_ON failed.'),
        original_hdi_init_lookup_successes=hilog.count('hdiInit ret:0'),
        adapter_operation_entries=re.findall(r'NATIVE_BT022 op=operation_entry result=(-?\d+)', text),
        pairing_verified=False, nearby_discovery_verified=False,
        bluetooth_acceptance_not_inferred=True, disk_validation_suite_rerun=False)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
