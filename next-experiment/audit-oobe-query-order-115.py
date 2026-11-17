"""Verify within-boot query ordering and reference service-selection differences."""
from pathlib import Path
import ast
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = Path('/mnt/c/Users/39255/AppData/Local/Temp/opencode/HarmonyMac-reference-816')


def milliseconds(line):
    match = re.match(rb'11-16 (\d\d):(\d\d):(\d\d)\.(\d{3}) ', line)
    assert match, 'Do not mix wall-clock epochs'
    h, m, s, ms = map(int, match.groups())
    return ((h * 60 + m) * 60 + s) * 1000 + ms


if __name__ == '__main__':
    output = ROOT / 'reports/oobe-query-order-115.json'
    assert not output.exists()
    folder = ROOT / 'reports/commercial61-native-114'
    manifest = json.loads((folder / 'runtime-evidence/retrieval-manifest.json').read_text())
    log = (folder / 'runtime-evidence/raw/interactive-hilog030.log').read_bytes()
    assert hashlib.sha256(log).hexdigest() == manifest['files']['interactive-hilog030.log']['sha256']
    restart = json.loads((folder / 'oobe-scene-restart-analysis.json').read_text())
    old, new = restart['initial_scene_pid'], restart['replacement_scene_pid']
    rules = {
        'first_query_start': (' ' + str(old) + '  ' + str(old) + ' I C04613/').encode(),
        'initialization_complete': b'RegisterHichainProofExceptionStatusCallback, ret: 0',
        'replacement_query_start': (' ' + str(new) + '  ' + str(new) + ' I C04613/').encode(),
        'replacement_query_end': (' ' + str(new) + '  ' + str(new) + ' I C04613/').encode(),
    }
    suffixes = {'first_query_start': b'CFWKProxy: [device_picker_client.cpp:388]GetTrustedDeviceListWithAbilityFilter# start',
                'replacement_query_start': b'CFWKProxy: [device_picker_client.cpp:388]GetTrustedDeviceListWithAbilityFilter# start',
                'replacement_query_end': b'CFWKProxy: [device_picker_client.cpp:396]GetTrustedDeviceListWithAbilityFilter# end'}
    found = {}
    for name, needle in rules.items():
        rows = [(i, line) for i, line in enumerate(log.splitlines(), 1)
                if len(line) < 4096 and needle in line and (name not in suffixes or suffixes[name] in line)]
        assert len(rows) == 1, (name, len(rows))
        i, line = rows[0]
        found[name] = dict(line=i, milliseconds=milliseconds(line), text=line.decode())
    assert found['first_query_start']['milliseconds'] < found['initialization_complete']['milliseconds']
    assert found['initialization_complete']['milliseconds'] < found['replacement_query_start']['milliseconds']
    duration = found['replacement_query_end']['milliseconds'] - found['replacement_query_start']['milliseconds']
    assert duration == 7
    revision = subprocess.check_output(['git', '-C', str(REFERENCE), 'rev-parse', 'HEAD'], text=True).strip()
    assert revision == 'f23a5d73f86ef0e45d3e7ac879a0605049a3c9ad'
    enable = REFERENCE / 'ports/tools/enable-local-services.py'
    tree = ast.parse(enable.read_text())
    choices = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'add_argument':
            if node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value == 'services':
                choices = ast.literal_eval(next(keyword.value for keyword in node.keywords if keyword.arg == 'choices'))
    assert 'device_manager' in choices and 'CollaborationFwk' not in choices
    sources = ['ports/tools/adapt-local-root.py', 'ports/tools/enable-local-services.py',
               'ports/tests/native-desktop-start.sh']
    result = dict(run=manifest['run'], hilog_sha256=manifest['files']['interactive-hilog030.log']['sha256'],
        events=found, replacement_query_duration_ms=duration,
        original_freeze_kill_proven=restart['original_appms_freeze_kill_proven'],
        reference_revision=revision, reference_explicit_service_choices=choices,
        reference_source_hashes={name: hashlib.sha256((REFERENCE / name).read_bytes()).hexdigest() for name in sources},
        helper_does_not_offer_collaboration_service=True,
        reference_final_successful_runtime_service_inventory_not_available_here=True,
        absence_from_helper_choices_not_proof_of_runtime_service_absence=True,
        next_test='Gate existing early Home launcher on current original CollaborationFwk initialization event; preserve all original services and checks',
        startup_dependency_may_prevent_gate_completion=True,
        original_query_result_or_activation_state_modified=False, target_boot_performed=False,
        desktop_verified=False)
    output.open('x').write(json.dumps(result, indent=2))
    print(json.dumps(dict(run=manifest['run'], events=found, replacement_query_duration_ms=duration,
                         original_services_modified=False, target_boot_performed=False), indent=2))
