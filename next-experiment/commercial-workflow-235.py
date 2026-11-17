"""One repaired-provider boot, using the admitted206 preservation/transport workflow."""
from pathlib import Path
import json
import runpy
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
REPORT = ROOT / 'reports/commercial61-native-235'
OPERATIONS = ('install-commercial-native', 'run-commercial-native', 'retrieve-commercial-evidence', 'verify-commercial-return')
configure_local_transport = runpy.run_path(str(BASE / 'commercial-workflow-043.py'))['configure_local_transport']


def source235(operation):
    assert operation in OPERATIONS
    source = (ROOT / 'reports/commercial61-native-206' / (operation + '.generated.py')).read_text()
    for old, new in [
        ('commercial61-native-206', 'commercial61-native-235'),
        ('commercial-return-audit-206', 'commercial-return-audit-235'),
        ('ordered_chain_equals_full_206', 'ordered_chain_equals_full_235'),
        ('settings206_preflight', 'settings235_preflight'), ('estimated206', 'estimated235'),
        ('set206.img', 'set235.img'),
        ('native original BMS recovery and readiness-gated Settings 206 - AUTO RETURN 270 SEC',
         'native SettingsData scaffolding and lifecycle diagnostics 235 - AUTO RETURN 900 SEC')]:
        source = source.replace(old, new)
    repair = json.loads((ROOT / 'reports/settingsdata-orphan-repair-234/result.json').read_text())
    old_data = 'e7e18b21f4e1d0d6a4acd652edc13b64c0ab4f3540ea6ddb155ea107f4e57fb4'
    if operation in ['install-commercial-native', 'run-commercial-native']:
        assert source.count(old_data) == 1
        source = source.replace(old_data, repair['candidate_after_sha256'], 1)
    if operation == 'run-commercial-native':
        old = json.loads((ROOT / 'reports/commercial61-native-206/overlay-result.json').read_text())['sha256']
        new = json.loads((REPORT / 'overlay-result.json').read_text())['sha256']
        assert source.count(old) == 1
        source = source.replace(old, new, 1)
    elif operation == 'retrieve-commercial-evidence':
        run = json.loads((ROOT / 'reports/commercial61-native-206/runtime-evidence/retrieval-manifest.json').read_text())['run']
        anchor = 'if p.name not in ['
        assert source.count(anchor) == 1 and run not in source
        source = source.replace(anchor, anchor + repr(run) + ', ', 1)
        line = "with (dest/'original.tar').open('xb') as f:f.write(r.stdout)\n"
        assert source.count(line) == 1
        source = source.replace(line, '', 1)
        anchor = ' run=runs[0]\n'
        assert source.count(anchor) == 1
        source = source.replace(anchor, anchor + " phases=[p for p in run.glob('phase-*.log') if p.is_file()]\n assert 0<len(phases)<=2,'successful cumulative snapshot retention bound failed'\n", 1)
        anchor = "manifest=json.loads(r.stderr.decode().splitlines()[0])\n"
        assert source.count(anchor) == 1
        source = source.replace(anchor, anchor + "manifest['original_tar_not_persisted']=True\nmanifest['successful_cumulative_snapshots_retained']=2\n", 1)
    return source


if __name__ == '__main__':
    assert len(sys.argv) == 2 and sys.argv[1] in (*OPERATIONS, 'retain-entries')
    admission = json.loads((REPORT / 'admission-test.json').read_text())
    assert admission and all(admission.values())
    repair = json.loads((ROOT / 'reports/settingsdata-orphan-repair-234/result.json').read_text())
    assert repair['final_read_only_fsck_exit'] == 0 and repair['active165_sha256_verified_unchanged']
    configure_local_transport()
    if sys.argv[1] == 'retain-entries':
        path = BASE / 'retain-latest-experiment-boot-entries-001.py'
        source = path.read_text()
        assert source.count('commercial[-2:]') == 1
        source = source.replace('commercial[-2:]',
            "[p for p in commercial if p.name in {'commercial61-native-173.conf','commercial61-native-235.conf'}]", 1)
        source = source.replace('assert all((entries/n).is_file() for n in keep)',
            'assert len(keep)==4 and all((entries/n).is_file() for n in keep)', 1)
        exec(compile(source, str(path), 'exec'), {'__name__': '__main__', '__file__': str(path)})
    else:
        operation = sys.argv[1]
        source = source235(operation)
        assert source == (REPORT / (operation + '.generated.py')).read_text()
        exec(compile(source, operation, 'exec'),
            {'__name__': '__main__', '__file__': str(BASE / (operation + '-235.py'))})
