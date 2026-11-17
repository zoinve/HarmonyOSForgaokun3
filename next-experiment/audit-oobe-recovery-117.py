"""Read-only correlation of the original recovery predicates and run 116."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]


def predicate_destination(instructions, start, stop, value):
    """Evaluate only the decoded boolean normalization and branch block."""
    by_offset = {item['offset']: item for item in instructions}
    following = {a['offset']: b['offset'] for a, b in zip(instructions, instructions[1:])}
    pc, accumulator = start, value
    for _ in range(16):
        item = by_offset[pc]
        name = item['name']
        next_pc = following[pc]
        if name == 'callruntime.istrue':
            accumulator = accumulator is True
        elif name == 'callruntime.isfalse':
            accumulator = accumulator is False
        elif name == 'ldtrue':
            accumulator = True
        elif name == 'ldfalse':
            accumulator = False
        elif name == 'jnez':
            if accumulator:
                next_pc = item['target']
        elif name == 'jmp':
            next_pc = item['target']
        else:
            raise AssertionError((pc, name))
        if pc == stop:
            return next_pc
        pc = next_pc
    raise AssertionError('Unexpected predicate control flow')


def main():
    out = ROOT / 'reports/oobe-recovery-117'
    assert not out.exists(), 'Preserve numbered evidence'
    source = ROOT / 'reports/sceneboard-oobe-audit-097/decoded-methods.json'
    decoded = json.loads(source.read_bytes())
    matches = [m for m in decoded['methods'] if 'BaseOobeManager&' in m['record']
               and m['method']['name'] == '#~@0=@0*#']
    assert len(matches) == 1
    callback = matches[0]
    instructions = callback['instructions']
    truth_table = []
    for active in (False, True):
        for trusted in (False, True):
            first = predicate_destination(instructions, 38, 50, active)
            assert first == (80 if active else 52)
            second = predicate_destination(instructions, 100, 112, trusted)
            assert second == (142 if trusted else 114)
            action = 'restart_oobe' if first == 80 and second == 142 else 'return'
            truth_table.append(dict(oobe_active=active, trustlist_match=trusted, action=action))
    folder = ROOT / 'reports/commercial61-native-116/runtime-evidence'
    manifest = json.loads((folder / 'retrieval-manifest.json').read_bytes())
    name = 'interactive-hilog030.log'
    raw = (folder / 'raw' / name).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == manifest['files'][name]['sha256']
    assert len(raw) == manifest['files'][name]['bytes']
    # Only fixed OOBE messages are exported, not unrelated device identifiers.
    markers = (
        b'init ok, provisioned: 0, isOobeEnable: true',
        b'user[100] oobe settings data changed, isOobeEnable: true',
        b'sessionExceptionCallback is called',
        b'isTrustlistForWms key: com.huawei.hmos.hwstartupguide:pc_hwstartupguide:com.huawei.hmos.hwstartupguide.MainAbility res: true',
        b'BaseOobeManager: start oobe again',
    )
    observations = []
    for number, line in enumerate(raw.splitlines(), 1):
        for marker in markers:
            if marker in line:
                observations.append(dict(line=number, timestamp=line[:18].decode('ascii'),
                                         message=marker.decode('ascii')))
    assert all(any(m.decode('ascii') == row['message'] for row in observations) for m in markers)
    assert any(row['timestamp'] == '11-16 02:06:24.531' and row['message'] == markers[3].decode('ascii')
               for row in observations)
    bms = next(m for m in decoded['methods'] if 'SCBOobeManager&' in m['record']
               and m['method']['name'] == '#~@0>#getOobeEnableByBms')
    strings = {o.get('string') for i in bms['instructions'] for o in i['operands']}
    assert {'isStartupGuideInstalled', 'setApplicationEnabled', 'setOobeMainAbilityEnable'} <= strings
    result = dict(run=manifest['run'], input_sha256={
        str(source.relative_to(ROOT)): hashlib.sha256(source.read_bytes()).hexdigest(),
        name: digest}, original_hap_sha256=decoded['hap_sha256'],
        callback_instruction_sha256=callback['method']['instruction_sha256'],
        boolean_branch_truth_table=truth_table, runtime_observations=observations,
        bms_initialization_reenables_installed_guide=True,
        commercial_activation_not_inferred_from_isOobeActivated=True,
        full_native_non_oobe_mode_proven=False,
        reference_success_runtime_configuration_available=False,
        operational_boot_performed=False, original_images_modified=False,
        desktop_verified=False,
        next_required_evidence='Accepted HarmonyMac current-config and SceneBoard lifecycle logs; '
            'compare package hashes, listener registration and state at its successful stop. '
            'Do not repeat force-stop or disable applications without a changed-condition hypothesis.')
    out.mkdir()
    with (out / 'result.json').open('x') as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
